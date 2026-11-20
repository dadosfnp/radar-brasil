import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from apps.indicadores.models import RegistroParametro, TraducaoCache


class PainelMultinivelAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_eixo_valido_retorna_200(self):
        for eixo in ["Governanca", "Politicas e Planos", "Programas", "Linhas de Financiamento"]:
            res = self.client.get(reverse("indicadores:painel_multinivel_api"), {"eixo": eixo})
            self.assertEqual(res.status_code, 200, f"eixo={eixo}")
            self.assertEqual(res["Content-Type"], "application/json")

    def test_eixo_invalido_retorna_400(self):
        res = self.client.get(reverse("indicadores:painel_multinivel_api"), {"eixo": "invalido"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("erro", res.json())

    def test_sem_eixo_usa_default_governanca(self):
        res = self.client.get(reverse("indicadores:painel_multinivel_api"))
        self.assertEqual(res.status_code, 200)


class VisaoGeralPainelTest(TestCase):
    """Nível Eixo, peso e descrições do Painel ▸ Visão Geral (2026-11-16)."""

    def setUp(self):
        self.client = Client()
        dados = [
            ("Operacionalidade", ["Nível 2", "Nível 2", "Nível 4", "Nível 4"]),
            ("Espaço de diálogo federativo", ["Nível 3", "Nível 3", "Nível 3"]),
            ("Financiamento", ["Nível 2", "Nível 2"]),
            ("Representação de Gênero, Raça e Etnia", ["Nível 1", "Nível 1", "Nível 1"]),
            ("Comunicação e Transparência", ["Nível 5", "Nível 5"]),
        ]
        for avaliacao, niveis in dados:
            for nivel in niveis:
                RegistroParametro.objects.create(
                    lang="pt",
                    estrutura="",
                    eixo="governanca",
                    avaliacao=avaliacao,
                    nivel=nivel,
                )

    def test_nivel_eixo_e_media_simples_dos_criterios(self):
        res = self.client.get(reverse("indicadores:painel_multinivel_api"), {"eixo": "Governanca"})
        corpo = res.json()
        # (3.0 + 3.0 + 2.0 + 1.0 + 5.0) / 5 = 2.8, arredondado pra numero redondo (3)
        # — pedido do usuario em 2026-11-20, "3/5" em vez de "2.8/5"
        self.assertEqual(corpo["nivel_eixo"], 3)
        self.assertEqual(corpo["total_componentes"], 4)
        self.assertTrue(corpo["descricao_eixo"])

    def test_criterios_tem_descricao_peso_e_nivel_medio(self):
        res = self.client.get(reverse("indicadores:painel_multinivel_api"), {"eixo": "Governanca"})
        por_nome = {c["nome"]: c for c in res.json()["criterios"]}

        self.assertEqual(por_nome["Operacionalidade"]["nivel_medio"], 3.0)
        self.assertEqual(por_nome["Operacionalidade"]["peso"], 1)

        # "peso 2" só no Espaço de diálogo federativo (Governança)
        self.assertEqual(por_nome["Espaço de diálogo federativo"]["peso"], 2)

        # "Financiamento" vira "Sustentabilidade Financeira" no eixo Governança
        self.assertIn("Sustentabilidade Financeira", por_nome)
        self.assertEqual(por_nome["Sustentabilidade Financeira"]["nivel_medio"], 2.0)
        self.assertEqual(por_nome["Sustentabilidade Financeira"]["peso"], 1)

        for criterio in por_nome.values():
            self.assertTrue(criterio["descricao"], f"sem descricao: {criterio['nome']}")

    def test_criterio_de_genero_raca_etnia_em_en_e_renomeado_e_tem_descricao(self):
        # Achado real (2026-11-16): a chave de rename em EN usava a ordem de palavras
        # errada ("Gender, Race and Ethnicity Representation") e nunca batia com o
        # valor de verdade salvo no banco ("Representation of Gender, Race and
        # Ethnicity") — o criterio nunca era renomeado nem ganhava descricao em EN.
        from apps.indicadores.services.painel_multinivel import dados_para_grafico

        RegistroParametro.objects.create(
            lang="en",
            estrutura="",
            eixo="governanca",
            avaliacao="Representation of Gender, Race and Ethnicity",
            nivel="Nível 2",
        )
        corpo = dados_para_grafico("Governanca", lang="en")
        self.assertNotIn("Representation of Gender, Race and Ethnicity", corpo["labels"])
        por_nome = {c["nome"]: c for c in corpo["criterios"]}
        self.assertIn("Diversity and Representativeness", por_nome)
        self.assertTrue(por_nome["Diversity and Representativeness"]["descricao"])


class AvaliacaoAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_filtros_eixo_valido_retorna_200(self):
        res = self.client.get(reverse("indicadores:api_avaliacao_filtros"), {"eixo": "Governanca"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/json")

    def test_filtros_eixo_invalido_retorna_400(self):
        res = self.client.get(reverse("indicadores:api_avaliacao_filtros"), {"eixo": "xpto"})
        self.assertEqual(res.status_code, 400)

    def test_tabela_sem_estrutura_retorna_lista_vazia(self):
        res = self.client.get(reverse("indicadores:api_avaliacao_tabela"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"rows": []})

    def test_ficha_sem_estrutura_retorna_lista_vazia(self):
        res = self.client.get(reverse("indicadores:api_avaliacao_ficha"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"campos": []})


class MapaAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_filtros_mapa_retorna_200(self):
        res = self.client.get(reverse("indicadores:api_mapa_filtros"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/json")

    def test_dados_mapa_retorna_200(self):
        res = self.client.get(reverse("indicadores:api_mapa_dados"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/json")


class FinanciamentoAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_filtros_retorna_200(self):
        res = self.client.get(reverse("indicadores:api_fin_cli_filtros"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/json")

    def test_tabela_sem_filtros_retorna_rows(self):
        res = self.client.get(reverse("indicadores:api_fin_cli_tabela"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("rows", data)

    def test_tabela_parametros_injetados_nao_quebram(self):
        res = self.client.get(
            reverse("indicadores:api_fin_cli_tabela"),
            {"programa": "'; DROP TABLE --", "setor": "<script>alert(1)</script>"},
        )
        self.assertIn(res.status_code, [200, 400, 500])
        self.assertEqual(res["Content-Type"], "application/json")


class PaginasViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_paginas_renderizam_200(self):
        urls = [
            reverse("indicadores:painel_multinivel"),
            reverse("indicadores:avaliacao_painel"),
            reverse("indicadores:mapa_georreferenciado"),
            reverse("indicadores:nota_pais"),
            reverse("indicadores:financiamento_climatico"),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"url={url}")


class CorrigirMojibakeTest(TestCase):
    def test_corrige_acentos_e_pontuacao_e_preserva_texto_limpo(self):
        from apps.indicadores.services.sheets_reader import _corrigir_mojibake as fix

        # UTF-8 lido como Latin-1 (controles C1) e como cp1252
        self.assertEqual(fix("S\u00c3\u00a3o Lu\u00c3\u00ads"), "São Luís")
        self.assertEqual(fix("\u00c3\u0081frica e \u00c3\u0081sia"), "África e Ásia")
        self.assertEqual(
            fix("Bus corridor \u00e2\u0080\u0093 Av. Central"), "Bus corridor – Av. Central"
        )
        self.assertEqual(fix("the entity\u00e2\u20ac\u2122s ability"), "the entity’s ability")
        # espaco invisivel corrompido (e o proprio) some
        self.assertEqual(fix("Port of Sergipe\u00e2\u0080\u008b"), "Port of Sergipe")
        # celula com acento legitimo e trecho corrompido: corrige so o trecho
        self.assertEqual(fix("Câmara \u00e2\u0080\u0093 São Paulo"), "Câmara – São Paulo")
        # texto limpo nao muda
        for limpo in (
            "PAVIMENTAÇÃO",
            "Câmara Técnica",
            "âmbito",
            "Âmbito federal",
            "Ação",
            42,
            None,
        ):
            self.assertEqual(fix(limpo), limpo)


def _resposta_json(payload: dict):
    return SimpleNamespace(text=json.dumps(payload, ensure_ascii=False))


class TraducaoTest(TestCase):
    def test_criterio_en_e_es_tem_as_mesmas_chaves(self):
        from apps.indicadores.services.traducao import CRITERIO_EN, CRITERIO_ES

        self.assertEqual(set(CRITERIO_EN.keys()), set(CRITERIO_ES.keys()))
        self.assertEqual(len(CRITERIO_EN), 12)

    @patch.dict("os.environ", {"GEMINI_API_KEY": ""})
    def test_sem_chave_devolve_texto_em_pt_sem_gravar_cache(self):
        from apps.indicadores.services.traducao import traduzir_textos

        resultado = traduzir_textos({"Texto qualquer"}, "en")
        self.assertEqual(resultado, {"Texto qualquer": "Texto qualquer"})
        self.assertEqual(TraducaoCache.objects.count(), 0)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.indicadores.services.traducao.genai.Client")
    def test_traduz_e_grava_no_cache(self, Client):
        from apps.indicadores.services.traducao import traduzir_textos, _hash

        # traduzir_textos ordena os textos (sorted) antes de montar o lote — "Mundo" < "Olá"
        Client.return_value.models.generate_content.return_value = _resposta_json(
            {"0": "World", "1": "Hello"}
        )
        resultado = traduzir_textos({"Olá", "Mundo"}, "en")
        self.assertEqual(resultado, {"Olá": "Hello", "Mundo": "World"})
        self.assertEqual(TraducaoCache.objects.count(), 2)
        self.assertTrue(TraducaoCache.objects.filter(hash_origem=_hash("Olá"), lang="en").exists())

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.indicadores.services.traducao.genai.Client")
    def test_segunda_chamada_usa_cache_sem_chamar_gemini_de_novo(self, Client):
        from apps.indicadores.services.traducao import traduzir_textos

        Client.return_value.models.generate_content.return_value = _resposta_json({"0": "Hello"})
        traduzir_textos({"Olá"}, "en")
        self.assertEqual(Client.return_value.models.generate_content.call_count, 1)

        traduzir_textos({"Olá"}, "en")
        self.assertEqual(Client.return_value.models.generate_content.call_count, 1)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.indicadores.services.traducao.genai.Client")
    def test_lote_com_todos_os_modelos_falhando_nao_grava_cache(self, Client):
        from apps.indicadores.services.traducao import traduzir_textos

        Client.return_value.models.generate_content.side_effect = RuntimeError("503")
        resultado = traduzir_textos({"Olá"}, "en")
        self.assertEqual(resultado, {"Olá": "Olá"})
        self.assertEqual(TraducaoCache.objects.count(), 0)

    def test_extrair_json_remove_cerca_markdown(self):
        from apps.indicadores.services.traducao import _extrair_json

        bruto = '```json\n{"0": "ok"}\n```'
        self.assertEqual(_extrair_json(bruto), {"0": "ok"})

    def test_extrair_json_sem_texto_lanca_erro_tratavel(self):
        from apps.indicadores.services.traducao import _extrair_json

        with self.assertRaises(ValueError):
            _extrair_json(None)
