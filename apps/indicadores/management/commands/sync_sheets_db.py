"""
Importa dados do Google Sheets para o banco PostgreSQL.

Uso:
    python manage.py sync_sheets_db                   # importa tudo
    python manage.py sync_sheets_db --sheet fichas    # só fichas (PT + EN)
    python manage.py sync_sheets_db --lang en         # só idioma EN
    python manage.py sync_sheets_db --sheet mapa --lang pt
"""

import re
import unicodedata

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.indicadores.models import (
    NotaCalculada,
    RegistroFicha,
    RegistroFinanciamento,
    RegistroMapa,
    RegistroParametro,
)
from apps.indicadores.services import sheets_reader as sr
from apps.indicadores.services import traducao as tr


def _s(v) -> str:
    s = str(v).strip()
    return "" if s in ("nan", "None", "N/A") else s


def _normalizar(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", str(texto))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def _normalizar_quebras(v: str) -> str:
    return v.replace("\r\n", "\n").replace("\r", "\n")


def _multiline(v: str) -> str:
    """Normaliza quebras e detecta itens concatenados sem separador (padrão EN)."""
    v = _normalizar_quebras(v)
    if "\n" not in v and len(v) > 50:
        v = re.sub(r"(?<=[a-z])(?=[A-Z])", "\n", v)
    return v


def _parse_pct(v) -> float:
    try:
        if v in (None, "", "nan"):
            return 0.0
        s = str(v).strip()
        if s.endswith("%"):
            s = s[:-1].strip()
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        f = float(s)
    except (TypeError, ValueError):
        return 0.0
    return round(f * 100, 1) if 0 < f <= 1 else round(f, 1)


def _parse_est(v) -> float:
    try:
        return float(str(v).strip() or 0)
    except (ValueError, TypeError):
        return 0.0


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None


def extrair_notas_calculo(valores: list) -> list:
    """Extrai (eixo normalizado, posicao, nota) das linhas "Nível Eixo – <eixo>" da aba CALCULO.

    Cada bloco da aba tem um cabeçalho "ID | Componente | Fr | XXX-C01 … XXX-C0n | NÍVEL …"
    e termina numa linha de totais "Nível Eixo – <eixo>". As colunas XXX-Cnn dessa linha
    são os critérios (posicao 1..n); a coluna logo depois do último critério é a nota do
    eixo (posicao 0).
    """
    notas = []
    cabecalho = None
    for linha in valores:
        primeira = str(linha[0]).strip() if linha else ""
        if primeira == "ID":
            cabecalho = [str(c).strip() for c in linha]
            continue
        if not primeira.startswith("Nível Eixo") or cabecalho is None:
            continue
        eixo = _normalizar(re.split(r"[–-]", primeira, maxsplit=1)[1])
        cols = [i for i, c in enumerate(cabecalho) if re.search(r"-C\d+$", c)]
        if not cols:
            raise ValueError(f"CALCULO: bloco '{primeira}' sem colunas de critério")
        for posicao, i in enumerate(cols + [cols[-1] + 1], start=1):
            notas.append(
                {
                    "eixo": eixo,
                    # nota do eixo (coluna depois do último critério) vai pra posicao 0
                    "posicao": 0 if posicao > len(cols) else posicao,
                    "nota": float(str(linha[i]).replace(",", ".")),
                }
            )
        cabecalho = None
    return notas


class Command(BaseCommand):
    help = "Importa dados do Google Sheets para o PostgreSQL (radar_brasil)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sheet",
            choices=["fichas", "parametros", "financiamento", "mapa", "calculo", "all"],
            default="all",
            help="Planilha a importar (default: all)",
        )
        parser.add_argument(
            "--lang",
            choices=["pt", "en", "es", "all"],
            default="all",
            help="Idioma a importar (default: all)",
        )

    def handle(self, *args, **options):
        sheet = options["sheet"]
        lang = options["lang"]

        sheets = (
            ["fichas", "parametros", "financiamento", "mapa", "calculo"]
            if sheet == "all"
            else [sheet]
        )
        langs = ["pt", "en", "es"] if lang == "all" else [lang]
        # Espanhol existe (via traducao automatica, ver traducao.py) para Fichas,
        # Parametros e Financiamento — Mapa ainda nao tem planilha nem fonte ES.
        sem_es = {"mapa"}

        for s in sheets:
            if s == "calculo":
                # So numeros, sem idioma: importa uma vez, independente de --lang
                self.stdout.write("\n→ Importando calculo...")
                self._importar_calculo()
                self.stdout.write(self.style.SUCCESS("  ✓ calculo concluído"))
                continue
            for lg in langs:
                if lg == "es" and s in sem_es:
                    self.stdout.write(f"\n… {s} [es] ainda nao suportado, pulando")
                    continue
                self.stdout.write(f"\n→ Importando {s} [{lg}]...")
                try:
                    getattr(self, f"_importar_{s}")(lg)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {s} [{lg}] concluído"))
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f"  ✗ {s} [{lg}]: {exc}"))
                    raise

    # ── Fichas ───────────────────────────────────────────────────
    # Campos traduziveis (texto livre, via traducao.py) — tudo que nao e link nem eixo.
    _CAMPOS_TRADUZIVEIS_FICHA = [
        "estrutura",
        "setor",
        "descricao",
        "orgao_responsavel",
        "arcabouco_normativo",
        "espaco_dialogo_federativo",
        "financiamento",
        "periodicidade",
        "composicao",
        "carater_decisorio",
        "politica_plano_relacionado",
        "contrapartida",
        "modalidade",
        "repasse",
        "fontes",
    ]

    def _importar_fichas(self, lang: str):
        # Fichas PT e a unica fonte (planilha); EN/ES sao geradas por traducao automatica
        # a partir do PT — ver docstring de traducao.py.
        df = sr.ler_fichas("pt")
        RegistroFicha.objects.filter(lang=lang).delete()

        linhas = []
        for _, row in df.iterrows():
            estrutura = _s(row.get("Estrutura", ""))
            if not estrutura:
                continue

            def gv(col):
                return _s(row.get(col, ""))

            linhas.append(
                {
                    "eixo": gv("Eixo"),
                    "estrutura": estrutura,
                    "setor": gv("Setor"),
                    "link_eixo": gv("Link_eixo"),
                    "descricao": _multiline(gv("Descricao")),
                    "orgao_responsavel": _multiline(gv("Orgao_responsavel")),
                    "link_orgao": gv("Link_orgao"),
                    "arcabouco_normativo": _multiline(gv("Arcabouco_normativo")),
                    "link_arcabouco": gv("Link_arcabouco"),
                    "espaco_dialogo_federativo": _multiline(gv("Espaco_dialogo_federativo")),
                    "financiamento": _multiline(gv("Financiamento")),
                    "periodicidade": _multiline(gv("Periodicidade")),
                    "composicao": _multiline(gv("Composicao")),
                    "carater_decisorio": _multiline(gv("Carater_decisorio")),
                    "politica_plano_relacionado": _multiline(gv("Politica_Plano_relacionado")),
                    "contrapartida": _multiline(gv("Contrapartida")),
                    "modalidade": _multiline(gv("Modalidade")),
                    "repasse": _multiline(gv("Repasse")),
                    "fontes": _multiline(gv("Fontes")),
                }
            )

        if lang != "pt":
            textos = {
                v
                for linha in linhas
                for campo, v in linha.items()
                if campo in self._CAMPOS_TRADUZIVEIS_FICHA
            }
            traducoes = tr.traduzir_textos(textos, lang)
            for linha in linhas:
                for campo in self._CAMPOS_TRADUZIVEIS_FICHA:
                    if linha[campo]:
                        linha[campo] = traducoes.get(linha[campo], linha[campo])

        objs = [RegistroFicha(lang=lang, **linha) for linha in linhas]
        RegistroFicha.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} fichas importadas")

    # ── Parâmetros ───────────────────────────────────────────────
    _CAMPOS_TRADUZIVEIS_PARAMETRO = ["estrutura", "setor", "criterio", "descritivo"]

    def _importar_parametros(self, lang: str):
        # Parametros PT e a unica fonte (planilha); EN/ES sao geradas por traducao
        # automatica a partir do PT — ver docstring de traducao.py. "Avaliacao" usa
        # vocabulario fixo (CRITERIO_EN/CRITERIO_ES) em vez de traducao livre.
        df = sr.ler_parametros("pt")
        RegistroParametro.objects.filter(lang=lang).delete()

        linhas = []
        for _, row in df.iterrows():
            estrutura = _s(row.get("Estrutura", ""))
            if not estrutura:
                continue

            linhas.append(
                {
                    "eixo": _s(row.get("Eixo", "")),
                    "estrutura": estrutura,
                    "setor": _s(row.get("Setor", "")),
                    "nivel": _s(row.get("Nível", "")),
                    "criterio": _s(row.get("Critério", "")),
                    "avaliacao": _s(row.get("Avaliação", "")),
                    "classificacao": _s(row.get("Classificacao", "")),
                    "descritivo": _s(row.get("Descritivo", "")),
                }
            )

        if lang != "pt":
            dict_avaliacao = {"en": tr.CRITERIO_EN, "es": tr.CRITERIO_ES}[lang]
            textos = {
                v
                for linha in linhas
                for campo, v in linha.items()
                if campo in self._CAMPOS_TRADUZIVEIS_PARAMETRO
            }
            traducoes = tr.traduzir_textos(textos, lang)
            for linha in linhas:
                for campo in self._CAMPOS_TRADUZIVEIS_PARAMETRO:
                    if linha[campo]:
                        linha[campo] = traducoes.get(linha[campo], linha[campo])
                linha["avaliacao"] = dict_avaliacao.get(linha["avaliacao"], linha["avaliacao"])

        objs = [RegistroParametro(lang=lang, **linha) for linha in linhas]
        RegistroParametro.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} parâmetros importados")

    # ── Financiamento ────────────────────────────────────────────
    _CAMPOS_TRADUZIVEIS_FINANCIAMENTO = [
        "programa",
        "setor",
        "modalidade",
        "origem",
        "valor",
        "contrapartida",
        "federal",
        "estadual",
        "municipal",
        "ente",
    ]

    def _importar_financiamento(self, lang: str):
        # Financiamento Climatico PT e a unica fonte (aba Financiamento_climatico
        # da planilha V01, achado em 2026-11-18); EN/ES sao gerados por traducao
        # automatica a partir do PT, mesmo padrao de Fichas/Parametros — ver
        # docstring de traducao.py. Nenhum campo daqui e chave de lookup em outro
        # lugar do codigo, entao todos traduzem livremente (sem vocabulario fixo).
        df = sr.ler_financiamento("pt")
        RegistroFinanciamento.objects.filter(lang=lang).delete()

        prog_col = _col(df, "Programas e Linhas de Financiamento", "Programa", "Programas")
        setor_col = _col(df, "Setor")
        mod_col = _col(df, "Modalidade")
        orig_col = _col(df, "Origem dos Recursos", "Origem")
        val_col = _col(
            df, "Valor de financiamento", "Valor de Financiamento", "Valor do Financiamento"
        )
        cpart_col = _col(df, "Contrapatida mínima", "Contrapartida mínima", "Contrapartida")
        fed_col = _col(df, "Federal", "Repasse Federal")
        est_col = _col(df, "Estadual", "Repasse Estadual")
        mun_col = _col(df, "Municipal", "Repasse Municipal")
        ente_col = _col(df, "Tipo do repasse/financiamento", "Ente", "Ente Federado")

        def gv(row, col):
            if not col:
                return ""
            v = str(row.get(col, "")).strip()
            return "" if v in ("nan", "None", "N/A") else v

        linhas = []
        for _, row in df.iterrows():
            linhas.append(
                {
                    "programa": gv(row, prog_col),
                    "setor": gv(row, setor_col),
                    "modalidade": gv(row, mod_col),
                    "origem": gv(row, orig_col),
                    "valor": gv(row, val_col),
                    "contrapartida": gv(row, cpart_col),
                    "federal": gv(row, fed_col),
                    "estadual": gv(row, est_col),
                    "municipal": gv(row, mun_col),
                    "ente": gv(row, ente_col),
                }
            )

        if lang != "pt":
            textos = {
                v
                for linha in linhas
                for campo, v in linha.items()
                if campo in self._CAMPOS_TRADUZIVEIS_FINANCIAMENTO
            }
            traducoes = tr.traduzir_textos(textos, lang)
            for linha in linhas:
                for campo in self._CAMPOS_TRADUZIVEIS_FINANCIAMENTO:
                    if linha[campo]:
                        linha[campo] = traducoes.get(linha[campo], linha[campo])

        objs = [RegistroFinanciamento(lang=lang, **linha) for linha in linhas]
        RegistroFinanciamento.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} financiamentos importados")

    # ── Cálculo (notas oficiais) ─────────────────────────────────
    def _importar_calculo(self):
        notas = extrair_notas_calculo(sr.ler_calculo())
        eixos = {n["eixo"] for n in notas}
        if len(eixos) != 4:
            # Nao apaga as notas atuais se a aba veio incompleta/mudou de formato
            raise ValueError(f"CALCULO: esperava 4 eixos, achou {sorted(eixos)}")
        with transaction.atomic():
            NotaCalculada.objects.all().delete()
            NotaCalculada.objects.bulk_create([NotaCalculada(**n) for n in notas])
        for n in sorted(notas, key=lambda n: (n["eixo"], n["posicao"])):
            self.stdout.write(f"    {n['eixo']} [{n['posicao']}] = {n['nota']:.4f}")

    # ── Mapa ─────────────────────────────────────────────────────
    def _importar_mapa(self, lang: str):
        df = sr.ler_mapa(lang)
        RegistroMapa.objects.filter(lang=lang).delete()

        municipio_col = _col(df, "Municípios", "Municipios", "Município", "Municipio")
        estagio_col = _col(df, "Estágio", "Estagio")

        objs = []
        for _, row in df.iterrows():
            mun = str(row.get(municipio_col, "")).strip() if municipio_col else ""
            if not mun or mun == "nan":
                continue

            raw_code = str(row.get("code_muni", "")).strip()
            code_muni = str(int(float(raw_code))) if raw_code not in ("", "nan", "0") else ""

            etap = str(row.get(estagio_col, "")).strip() if estagio_col else ""
            pct = _parse_pct(row.get("Percentual_executado", 0))
            if pct == 0 and etap.lower() in ("concluído", "concluido"):
                pct = 100.0

            objs.append(
                RegistroMapa(
                    lang=lang,
                    code_muni=code_muni,
                    uf=str(row.get("UF", "")).strip(),
                    municipio=mun,
                    estagio=etap,
                    perfil=str(row.get("Perfil", "")).strip(),
                    estimativa_2023_2030=_parse_est(row.get("Estimativa_2023_2030", 0)),
                    populacao=str(row.get("Populacao", row.get("População", ""))).strip(),
                    empreendimento=str(row.get("Empreendimento", "")).strip(),
                    eixo=str(row.get("Eixo", "")).strip(),
                    modalidade=str(row.get("Modalidade", "")).strip(),
                    tipo_executor=str(row.get("Tipo de Executor", "")).strip(),
                    percentual_executado=pct,
                )
            )

        RegistroMapa.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} registros de mapa importados")
