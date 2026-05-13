# Financiamento Climático

Página do **Radar Brasil** que exibe informações sobre programas e linhas de financiamento climático no Brasil, com filtros interativos, gráficos e tabela paginada.

---

## Arquivos envolvidos

| Caminho | Responsabilidade |
|---|---|
| `templates/municipios/financiamento-climatico.html` | Estrutura HTML da página |
| `static/css/financiamento-climatico.css` | Estilos exclusivos da página |
| `static/js/financiamento-climatico.js` | Lógica de filtros, gráficos, tabela e exportação |
| `apps/indicadores/views.py` | Views Django (renderização + APIs JSON) |
| `apps/indicadores/urls.py` | Roteamento das URLs |
| `apps/indicadores/services/financiamento_climatico.py` | Leitura do Google Sheets + transformação dos dados |

---

## Roteamento

Prefixo base: `/indicadores/`

| URL | View | Descrição |
|---|---|---|
| `/indicadores/financiamento-climatico/` | `financiamento_climatico_view` | Renderiza o template |
| `/indicadores/api/financiamento/filtros/` | `api_fin_cli_filtros` | Retorna opções para os dropdowns |
| `/indicadores/api/financiamento/graficos/` | `api_fin_cli_graficos` | Retorna dados dos três gráficos |
| `/indicadores/api/financiamento/tabela/` | `api_fin_cli_tabela` | Retorna linhas da tabela |

Todas as APIs aceitam os mesmos query params de filtro: `programa`, `setor`, `modalidade`, `origem`, `ente`.

---

## Fonte de dados

Os dados são lidos de uma **planilha Google Sheets** via `gspread`:

- **Sheet ID:** `1lrT6g8JvB3wVZnlVK1JziffzW1mfSYSrGyOqsPZZJG4`
- **GID:** `992060842`
- **Credenciais:** `.secrets/fnp-radar-sheets.json` (Service Account)
- **Cache:** 30 minutos em memória (`CACHE_TTL = 1800`)

### Colunas esperadas na planilha

| Coluna (possíveis nomes) | Campo |
|---|---|
| `Programas e Linhas de Financiamento` / `Programa` / `Programas` | Programa |
| `Setor` | Setor |
| `Modalidade` | Modalidade |
| `Origem dos Recursos` / `Origem` | Origem |
| `Ente` / `Ente Federado` | Ente Federado |
| `Valor de Financiamento` / `Valor do Financiamento` | Valor monetário |
| `Contrapartida` / `Contrapartida mínima` | Contrapartida |
| `Federal` / `Repasse Federal` | Repasse Federal |
| `Estadual` / `Repasse Estadual` | Repasse Estadual |
| `Municipal` / `Repasse Municipal` | Repasse Municipal |

A função `_col(df, *names)` verifica qual nome de coluna existe no DataFrame, tornando a leitura tolerante a variações de nomenclatura.

---

## Serviço (`financiamento_climatico.py`)

### Funções públicas

#### `get_filtros() → dict`
Retorna as opções únicas de cada filtro:
```json
{
  "programas": [...],
  "setores": [...],
  "modalidades": [...],
  "origens": [...],
  "entes": [...]
}
```

#### `get_tabela(filtros: dict) → list[dict]`
Retorna as linhas filtradas para a tabela. Cada item:
```json
{
  "programa": "...", "setor": "...", "modalidade": "...",
  "origem": "...", "valor": "R$ 1,5 MI", "contrapartida": "...",
  "federal": "...", "estadual": "...", "municipal": "..."
}
```

#### `get_graficos(filtros: dict) → dict`
Retorna dados para os três gráficos:
```json
{
  "setor":  { "labels": [...], "values": [...], "texts": [...] },
  "origem": { "labels": [...], "values": [...], "colors": [...] },
  "ente":   { "labels": ["Federal","Estadual","Municipal"], "values": [...], "texts": [...] }
}
```

### Funções auxiliares internas

| Função | Descrição |
|---|---|
| `_ler_sheet()` | Lê o Google Sheets e armazena em cache |
| `_aplicar_filtros(df, filtros)` | Aplica os filtros recebidos por query param |
| `_parse_num(v)` | Converte string em float (suporta formato BRL: `R$ 1.000.000,00`) |
| `_fmt_brl(v)` | Formata número como string BRL (`R$ 1,5 MI`, `R$ 500 MIL`) |
| `_limpar(v)` | Remove espaços, `nan`, `None`, `N/A` |
| `_uniq(df, col)` | Retorna valores únicos e não-vazios de uma coluna |

---

## Frontend (`financiamento-climatico.js`)

### Classe `MultiSelect`
Dropdown com checkboxes, busca e seleção múltipla. Instâncias registradas em `msInstances`:

| Chave | ID do elemento | Filtro |
|---|---|---|
| `programa` | `#ms-programa` | Programa/Linha |
| `setor` | `#ms-setor` | Setor |
| `modalidade` | `#ms-modalidade` | Modalidade |
| `origem` | `#ms-origem` | Origem dos Recursos |
| `ente` | `#ms-ente` | Ente Federado |

**Semântica de seleção:** `selected` vazio = "todos"; ao clicar num item, ele é **excluído** do conjunto visível (os demais ficam selecionados).

### Fluxo de dados
```
DOMContentLoaded
  └─ _initMultiSelects()         inicializa dropdowns
  └─ carregarFiltros()           GET /api/financiamento/filtros/  → popula dropdowns
  └─ aplicarFiltros()
        ├─ carregarGraficos()    GET /api/financiamento/graficos/?<filtros>
        └─ carregarTabela()      GET /api/financiamento/tabela/?<filtros>

Ao mudar qualquer filtro → aplicarFiltros()
Botão "Limpar filtros" → limparFiltros() → aplicarFiltros()
Botão "Baixar Dados"  → baixarDados() → exporta CSV do allRows
Botão "Imprimir Tela" → window.print()
```

### Gráficos (Plotly.js 2.27)

#### Valor do Financiamento por Setor
- Tipo: **Barra vertical**
- Exibe os **top 5** setores ordenados por valor decrescente
- Container: `#fc-chart-setor`

#### Origem dos Recursos
- Tipo: **Barra horizontal** com scroll
- Container: `#fc-chart-origem` dentro de `.fc-origem-scroll` (max-height 280px)
- Ordenado do maior para o menor (Plotly inverte o eixo Y)
- Altura dinâmica: `n itens × 30px`

#### Repasse por Ente Federado
- Tipo: **Donut (pizza)**
- Labels: Federal, Estadual, Municipal
- Valores: soma dos valores monetários das colunas de repasse
- Container: `#fc-chart-ente`

### Tabela e paginação
- `ROWS_PER_PAGE = 10`
- Dados completos em `allRows[]`; paginação client-side
- Exportação CSV inclui BOM UTF-8 para compatibilidade com Excel

---

## Estrutura HTML resumida

```
.fc-page
├── .fc-intro              (título + descrição)
├── .fc-panel
│   ├── .fc-filters-bar    (5 MultiSelects)
│   ├── .fc-charts
│   │   ├── #fc-chart-setor       (barra vertical)
│   │   ├── .fc-origem-scroll
│   │   │   └── #fc-chart-origem  (barra horizontal)
│   │   └── #fc-chart-ente        (donut)
│   └── .fc-actions        (Limpar / Baixar / Imprimir)
└── .fc-table-wrap
    ├── #fc-loader
    ├── #fc-table
    │   ├── thead (2 linhas: grupos + sub-colunas)
    │   └── #fc-tbody
    └── #fc-pagination
```

---

## Dependências externas

| Biblioteca | Versão | Uso |
|---|---|---|
| Plotly.js | 2.27.0 (CDN) | Renderização dos gráficos |
| gspread | — | Leitura do Google Sheets |
| oauth2client | — | Autenticação Service Account |
| pandas | — | Transformação dos dados |
| Google Fonts — Sora | — | Tipografia dos títulos |
