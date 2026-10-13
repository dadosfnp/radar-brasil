import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from google.genai import errors

from apps.assistente.contexto import ler_faq, montar_contexto
from apps.assistente.ferramentas import consultar_mapa
from apps.assistente.models import InteracaoAssistente
from apps.assistente.servico import AssistenteIndisponivel, responder
from apps.indicadores.models import (
    RegistroFicha,
    RegistroFinanciamento,
    RegistroMapa,
    RegistroParametro,
)


class ContextoTest(TestCase):
    def setUp(self):
        RegistroFicha.objects.create(
            lang="pt",
            estrutura="Conselho da Federação (CF)",
            eixo="governanca",
            setor="Articulação",
            link_eixo="https://www.gov.br/sri",
            descricao="Cooperação entre os entes.",
            fontes="Ñ aplica",
        )
        RegistroParametro.objects.create(
            lang="pt",
            estrutura="Conselho da Federação (CF)",
            eixo="governanca",
            nivel="Nível 2",
            criterio="Baixo financiamento",
            avaliacao="Financiamento",
            descritivo="Sem dotação orçamentária.",
        )
        RegistroFinanciamento.objects.create(lang="pt", programa="Fundo Clima", valor="R$ 10 bi")

    def test_fontes_numeradas_com_titulo_eixo_e_link(self):
        ctx = montar_contexto("pt")
        self.assertEqual(
            ctx["fontes"]["F1"],
            {
                "titulo": "Conselho da Federação (CF)",
                "eixo": "Governança",
                "url": "https://www.gov.br/sri",
            },
        )
        self.assertEqual(ctx["fontes"]["L1"]["titulo"], "Fundo Clima")
        self.assertIn("[F1] Conselho da Federação (CF)", ctx["texto"])
        self.assertIn("[L1] Linha de financiamento: Fundo Clima", ctx["texto"])

    def test_usa_rotulos_de_exibicao_e_omite_campos_vazios(self):
        texto = montar_contexto("pt")["texto"]
        # "Financiamento" vira "Sustentabilidade Financeira" no eixo Governança
        self.assertIn("- Sustentabilidade Financeira: Nível 2 (Baixo financiamento)", texto)
        self.assertNotIn("Ñ aplica", texto)

    def test_faq_da_pagina_sobre_entra_como_fonte_nos_dois_idiomas(self):
        pt, en = ler_faq("pt"), ler_faq("en")
        self.assertGreaterEqual(len(pt), 9)
        self.assertEqual(len(pt), len(en))
        self.assertEqual(pt[1][0], "Qual a origem do Radar Brasil?")
        self.assertEqual(en[1][0], "What is the origin of Radar Brasil?")
        self.assertNotIn("{%", pt[1][1] + en[1][1])
        ctx = montar_contexto("pt")
        self.assertEqual(ctx["fontes"]["P2"]["titulo"], "Qual a origem do Radar Brasil?")

    def test_contexto_acompanha_novo_sync(self):
        self.assertNotIn("Novo Programa", montar_contexto("pt")["texto"])
        RegistroFinanciamento.objects.create(lang="pt", programa="Novo Programa")
        self.assertIn("Novo Programa", montar_contexto("pt")["texto"])


class ConsultarMapaTest(TestCase):
    def setUp(self):
        base = {"lang": "pt", "eixo": "Novo Pac - Mobilidade Urbana", "tipo_executor": "Municipal"}
        RegistroMapa.objects.create(
            uf="RJ", municipio="Niterói", estagio="Em execução", estimativa_2023_2030=100, **base
        )
        RegistroMapa.objects.create(
            uf="RJ", municipio="Niterói", estagio="Concluído", estimativa_2023_2030=50, **base
        )
        RegistroMapa.objects.create(
            uf="BA", municipio="Salvador", estagio="Concluído", estimativa_2023_2030=10, **base
        )

    def test_municipio_sem_acento_e_agregacao(self):
        r = consultar_mapa(municipio="niteroi")
        self.assertEqual(r["total_empreendimentos"], 2)
        self.assertEqual(r["investimento_estimado_2023_2030_reais"], 150)
        self.assertEqual(r["por_estagio"], {"Em execução": 1, "Concluído": 1})
        self.assertEqual(r["maiores_empreendimentos"][0]["estimativa_2023_2030_reais"], 100)

    def test_filtro_por_regiao_e_trecho_do_eixo(self):
        self.assertEqual(consultar_mapa(regiao="Nordeste")["total_empreendimentos"], 1)
        self.assertEqual(consultar_mapa(eixo="mobilidade")["total_empreendimentos"], 3)

    def test_sem_resultado(self):
        self.assertEqual(
            consultar_mapa(municipio="Xyzópolis"),
            {"filtros": {"municipio": "Xyzópolis"}, "total_empreendimentos": 0},
        )


def _resposta_gemini(texto):
    uso = SimpleNamespace(prompt_token_count=41000, candidates_token_count=80)
    return SimpleNamespace(text=texto, usage_metadata=uso)


class ResponderTest(TestCase):
    def setUp(self):
        RegistroFicha.objects.create(
            lang="pt", estrutura="Conselho da Federação (CF)", eixo="governanca"
        )

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.assistente.servico.genai.Client")
    def test_cita_so_fontes_existentes_e_envia_contexto(self, Client):
        criar = Client.return_value.chats.create
        criar.return_value.send_message.return_value = _resposta_gemini(
            "O CF é consultivo [F1][F999]. Niterói [MAPA]."
        )

        r = responder("O que é o CF?", [{"papel": "usuario", "texto": "oi"}], "pt")

        self.assertEqual([f["id"] for f in r["fontes"]], ["F1", "MAPA"])
        self.assertEqual(r["fontes"][0]["titulo"], "Conselho da Federação (CF)")
        self.assertEqual(r["tokens_entrada"], 41000)
        self.assertEqual(r["modelo"], "gemini-3.5-flash")
        config = criar.call_args.kwargs["config"]
        self.assertIn("[F1] Conselho da Federação (CF)", config.system_instruction)
        self.assertEqual(config.tools[0].__name__, "consultar_mapa")
        self.assertEqual(len(criar.call_args.kwargs["history"]), 1)
        criar.return_value.send_message.assert_called_once_with("O que é o CF?")

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.assistente.servico.genai.Client")
    def test_modelo_sobrecarregado_passa_para_a_reserva(self, Client):
        sobrecarga = errors.ServerError(
            503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "alta demanda"}}
        )
        Client.return_value.chats.create.return_value.send_message.side_effect = [
            sobrecarga,
            _resposta_gemini("ok [P1]"),
        ]
        r = responder("Pergunta", [], "pt")
        self.assertEqual(r["modelo"], "gemini-3.1-flash-lite")

    @patch.dict("os.environ", {"GEMINI_API_KEY": "teste"})
    @patch("apps.assistente.servico.genai.Client")
    def test_cota_esgotada_em_todos_os_modelos_vira_indisponivel(self, Client):
        Client.return_value.chats.create.return_value.send_message.side_effect = errors.ClientError(
            429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "cota"}}
        )
        with self.assertRaises(AssistenteIndisponivel):
            responder("Pergunta", [], "pt")

    @patch.dict("os.environ", {"GEMINI_API_KEY": ""})
    def test_sem_chave_vira_indisponivel(self):
        with self.assertRaises(AssistenteIndisponivel):
            responder("Pergunta", [], "pt")


class PerguntarAPITest(TestCase):
    url = reverse("assistente:perguntar")

    def _post(self, corpo, **extra):
        return self.client.post(
            self.url, json.dumps(corpo), content_type="application/json", **extra
        )

    @patch("apps.assistente.views.responder")
    def test_responde_e_registra_sem_ip_em_claro(self, responder_mock):
        responder_mock.return_value = {
            "resposta": "Resposta [P1]",
            "fontes": [{"id": "P1", "titulo": "FAQ", "eixo": "FAQ", "url": "/sobre/"}],
            "modelo": "gemini-teste",
            "tokens_entrada": 10,
            "tokens_saida": 5,
        }
        res = self._post({"pergunta": "O que é o Radar?"}, HTTP_X_REAL_IP="200.1.2.3")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["fontes"][0]["id"], "P1")
        reg = InteracaoAssistente.objects.get()
        self.assertEqual(reg.pergunta, "O que é o Radar?")
        self.assertEqual(len(reg.ip_hash), 64)
        self.assertNotIn("200.1.2.3", reg.ip_hash)

    def test_pergunta_vazia_ou_longa_retorna_400(self):
        self.assertEqual(self._post({"pergunta": "  "}).status_code, 400)
        self.assertEqual(self._post({"pergunta": "x" * 501}).status_code, 400)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    @patch("apps.assistente.views.LIMITE_IP_DIA", 2)
    @patch("apps.assistente.views.responder")
    def test_limite_diario_por_ip(self, responder_mock):
        responder_mock.return_value = {
            "resposta": "ok",
            "fontes": [],
            "modelo": "m",
            "tokens_entrada": 1,
            "tokens_saida": 1,
        }
        for _ in range(2):
            self.assertEqual(self._post({"pergunta": "a"}).status_code, 200)
        self.assertEqual(self._post({"pergunta": "a"}).status_code, 429)
        # outro visitante continua liberado
        self.assertEqual(self._post({"pergunta": "a"}, HTTP_X_REAL_IP="9.9.9.9").status_code, 200)

    @patch("apps.assistente.views.responder", side_effect=AssistenteIndisponivel("429 cota"))
    def test_provedor_indisponivel_retorna_503_e_nao_conta_no_limite(self, _):
        res = self._post({"pergunta": "a"})
        self.assertEqual(res.status_code, 503)
        self.assertEqual(InteracaoAssistente.objects.get().erro, "AssistenteIndisponivel: 429 cota")

    @patch("apps.assistente.views.responder", side_effect=ConnectionError("rede caiu"))
    def test_falha_inesperada_tambem_vira_503_em_json_e_fica_registrada(self, _):
        res = self._post({"pergunta": "a"})
        self.assertEqual(res.status_code, 503)
        self.assertIn("indisponível", res.json()["erro"])
        self.assertEqual(InteracaoAssistente.objects.get().erro, "ConnectionError: rede caiu")


class WidgetTest(TestCase):
    def test_paginas_tem_o_botao_do_chat_no_lugar_do_voltar_ao_topo(self):
        for nome in ("municipios:home", "municipios:sobre", "indicadores:mapa_georreferenciado"):
            html = self.client.get(reverse(nome)).content.decode()
            self.assertIn('id="as-botao"', html, nome)
            self.assertIn(reverse("assistente:perguntar"), html, nome)
            self.assertIn("mutiraobrasil@fnp.org.br", html, nome)
            self.assertNotIn("rb-scroll-top", html, nome)
