from django.test import TestCase

from apps.assistente.contexto import ler_faq, montar_contexto
from apps.assistente.ferramentas import consultar_mapa
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
