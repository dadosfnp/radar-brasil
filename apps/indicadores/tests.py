from django.test import TestCase, Client
from django.urls import reverse


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
