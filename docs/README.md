# Documentação Técnica — Radar Brasil

Esta pasta contém a documentação técnica das páginas desenvolvidas no projeto Radar Brasil.

## Páginas documentadas

| Arquivo | Página | URL |
|---|---|---|
| [financiamento-climatico.md](financiamento-climatico.md) | Financiamento Climático | `/indicadores/financiamento-climatico/` |
| [nota-pais.md](nota-pais.md) | Nota País | `/indicadores/nota-pais/` |

## Visão geral da arquitetura

```
radar-brasil/
├── apps/
│   └── indicadores/
│       ├── urls.py           Rotas das views e APIs
│       ├── views.py          Views Django (render + JsonResponse)
│       └── services/
│           ├── financiamento_climatico.py   Dados do Google Sheets
│           ├── painel_multinivel.py
│           ├── avaliacao_painel.py
│           └── mapa_georreferenciado.py
├── templates/
│   └── municipios/           Um template por página
├── static/
│   ├── css/                  Um CSS por página
│   └── js/                   Um JS por página
└── docs/                     ← você está aqui
```

## Padrão de desenvolvimento adotado

- **Uma responsabilidade por arquivo:** cada página tem seu próprio template, CSS e JS
- **APIs JSON sem estado:** todas as APIs recebem os filtros por query params e retornam dados calculados na hora (sem sessão)
- **Cache no serviço:** leituras do Google Sheets são cacheadas 30 min em memória para evitar chamadas repetidas
- **Dados embutidos no JS** quando não há backend de dados (ex: Nota País usa constantes JS para signatários e cores)
- **Classe do `<body>` separada da classe do wrapper de conteúdo** para evitar que estilos de layout do conteúdo vazar para o body
