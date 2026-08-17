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

from apps.indicadores.models import (
    RegistroFicha,
    RegistroFinanciamento,
    RegistroMapa,
    RegistroParametro,
)
from apps.indicadores.services import sheets_reader as sr


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


class Command(BaseCommand):
    help = "Importa dados do Google Sheets para o PostgreSQL (radar_brasil)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sheet",
            choices=["fichas", "parametros", "financiamento", "mapa", "all"],
            default="all",
            help="Planilha a importar (default: all)",
        )
        parser.add_argument(
            "--lang",
            choices=["pt", "en", "all"],
            default="all",
            help="Idioma a importar (default: all)",
        )

    def handle(self, *args, **options):
        sheet = options["sheet"]
        lang = options["lang"]

        sheets = ["fichas", "parametros", "financiamento", "mapa"] if sheet == "all" else [sheet]
        langs = ["pt", "en"] if lang == "all" else [lang]

        for s in sheets:
            for lg in langs:
                self.stdout.write(f"\n→ Importando {s} [{lg}]...")
                try:
                    getattr(self, f"_importar_{s}")(lg)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {s} [{lg}] concluído"))
                except Exception as exc:
                    self.stderr.write(self.style.ERROR(f"  ✗ {s} [{lg}]: {exc}"))
                    raise

    # ── Fichas ───────────────────────────────────────────────────
    def _importar_fichas(self, lang: str):
        df = sr.ler_fichas(lang)
        RegistroFicha.objects.filter(lang=lang).delete()

        objs = []
        for _, row in df.iterrows():
            estrutura = _s(row.get("Estrutura", ""))
            if not estrutura:
                continue

            def gv(col):
                return _s(row.get(col, ""))

            objs.append(
                RegistroFicha(
                    lang=lang,
                    estrutura=estrutura,
                    eixo=gv("Eixo"),
                    setor=gv("Setor"),
                    link_eixo=gv("Link_eixo"),
                    descricao=_multiline(gv("Descricao")),
                    orgao_responsavel=_multiline(gv("Orgao_responsavel")),
                    link_orgao=gv("Link_orgao"),
                    arcabouco_normativo=_multiline(gv("Arcabouco_normativo")),
                    link_arcabouco=gv("Link_arcabouco"),
                    espaco_dialogo_federativo=_multiline(gv("Espaco_dialogo_federativo")),
                    financiamento=_multiline(gv("Financiamento")),
                    periodicidade=_multiline(gv("Periodicidade")),
                    composicao=_multiline(gv("Composicao")),
                    carater_decisorio=_multiline(gv("Carater_decisorio")),
                    politica_plano_relacionado=_multiline(gv("Politica_Plano_relacionado")),
                    contrapartida=_multiline(gv("Contrapartida")),
                    modalidade=_multiline(gv("Modalidade")),
                    repasse=_multiline(gv("Repasse")),
                    fontes=_multiline(gv("Fontes")),
                )
            )

        RegistroFicha.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} fichas importadas")

    # ── Parâmetros ───────────────────────────────────────────────
    def _importar_parametros(self, lang: str):
        df = sr.ler_parametros(lang)
        RegistroParametro.objects.filter(lang=lang).delete()

        objs = []
        for _, row in df.iterrows():
            estrutura = _s(row.get("Estrutura", ""))
            if not estrutura:
                continue

            objs.append(
                RegistroParametro(
                    lang=lang,
                    estrutura=estrutura,
                    eixo=_s(row.get("Eixo", "")),
                    setor=_s(row.get("Setor", "")),
                    nivel=_s(row.get("Nível", "")),
                    criterio=_s(row.get("Critério", "")),
                    avaliacao=_s(row.get("Avaliação", "")),
                    classificacao=_s(row.get("Classificação", "")),
                    descritivo=_s(row.get("Descritivo", "")),
                )
            )

        RegistroParametro.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} parâmetros importados")

    # ── Financiamento ────────────────────────────────────────────
    def _importar_financiamento(self, lang: str):
        df = sr.ler_financiamento(lang)
        RegistroFinanciamento.objects.filter(lang=lang).delete()

        prog_col = _col(df, "Programas e Linhas de Financiamento", "Programa", "Programas")
        setor_col = _col(df, "Setor")
        mod_col = _col(df, "Modalidade")
        orig_col = _col(df, "Origem dos Recursos", "Origem")
        val_col = _col(
            df, "Valor de Financiamento", "Valor de financiamento", "Valor do Financiamento"
        )
        cpart_col = _col(df, "Contrapartida", "Contrapatida mínima", "Contrapartida mínima")
        fed_col = _col(df, "Federal", "Repasse Federal")
        est_col = _col(df, "Estadual", "Repasse Estadual")
        mun_col = _col(df, "Municipal", "Repasse Municipal")
        ente_col = _col(df, "Ente", "Ente Federado")

        objs = []
        for _, row in df.iterrows():

            def gv(col):
                if not col:
                    return ""
                v = str(row.get(col, "")).strip()
                return "" if v in ("nan", "None", "N/A") else v

            objs.append(
                RegistroFinanciamento(
                    lang=lang,
                    programa=gv(prog_col),
                    setor=gv(setor_col),
                    modalidade=gv(mod_col),
                    origem=gv(orig_col),
                    valor=gv(val_col),
                    contrapartida=gv(cpart_col),
                    federal=gv(fed_col),
                    estadual=gv(est_col),
                    municipal=gv(mun_col),
                    ente=gv(ente_col),
                )
            )

        RegistroFinanciamento.objects.bulk_create(objs, batch_size=500)
        self.stdout.write(f"    {len(objs)} financiamentos importados")

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
