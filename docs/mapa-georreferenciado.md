# Mapa Georreferenciado

Página do **Radar Brasil** que exibe os empreendimentos e investimentos climáticos distribuídos pelos municípios brasileiros em um mapa interativo com filtros encadeados e exportação de dados.

---

## Arquivos envolvidos

| Caminho | Responsabilidade |
|---|---|
| `templates/municipios/mapa-georreferenciado.html` | Estrutura HTML da página |
| `static/css/mapa-georreferenciado.css` | Estilos exclusivos da página |
| `static/js/mapa-georreferenciado.js` | Lógica do mapa Leaflet, filtros, popup e exportação |
| `apps/indicadores/views.py` | Views Django (renderização + APIs JSON) |
| `apps/indicadores/urls.py` | Roteamento das URLs |
| `apps/indicadores/services/mapa_georreferenciado.py` | Leitura do Google Sheets + transformação dos dados |

---

## Roteamento

Prefixo base: `/indicadores/`

| URL | View | Descrição |
|---|---|---|
| `/indicadores/mapa-georreferenciado/` | `mapa_georreferenciado_view` | Renderiza o template |
| `/indicadores/api/mapa/filtros/` | `api_mapa_filtros` | Retorna opções para os dropdowns |
| `/indicadores/api/mapa/dados/` | `api_mapa_dados` | Retorna GeoJSON com os pontos dos municípios |

---

## Dependências externas

| Biblioteca | Versão | Uso |
|---|---|---|
| Leaflet.js | 1.9.4 (CDN) | Mapa interativo e marcadores |
| html2canvas | 1.4.1 (CDN) | Captura de tela para Print Mapa |
| OpenStreetMap | — | Tiles do mapa base |
| Google Fonts — Sora | — | Tipografia dos títulos |

---

## Frontend (`mapa-georreferenciado.js`)

### Constantes globais

| Constante | Valor | Descrição |
|---|---|---|
| `COR_FINANCIAMENTO` | `#4CAF50` | Verde — município com financiamento |
| `COR_SEM_FINANCIAMENTO` | `#F4511E` | Laranja-vermelho — município sem financiamento |
| `BR_BOUNDS` | `LatLngBounds` | Limites aproximados do Brasil (restrição de pan/zoom) |
| `REGIAO_UFS` | Objeto | Mapeamento Região → array de siglas UF |
| `BRAZIL_POLY` | GeoJSON Feature | Polígono simplificado do Brasil (Natural Earth) para overlay |

#### `REGIAO_UFS`
```js
{
  "Norte":        ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
  "Nordeste":     ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
  "Centro-Oeste": ["DF", "GO", "MS", "MT"],
  "Sudeste":      ["ES", "MG", "RJ", "SP"],
  "Sul":          ["PR", "RS", "SC"],
}
```

### Variáveis de estado

| Variável | Tipo | Descrição |
|---|---|---|
| `map` | `L.Map` | Instância principal do Leaflet |
| `allFeatures` | `Array` | Todos os features GeoJSON carregados da API |
| `markerLayer` | `L.FeatureGroup` | Camada que contém os marcadores dos municípios |
| `canvasRenderer` | `L.Canvas` | Renderer canvas para performance com muitos pontos |
| `activeFilters` | `Object` | Estado atual dos filtros aplicados |
| `allUfOptions` | `Array<{value, text}>` | Cache de todas as opções de UF (para filtro cascata) |

---

### Funções principais

#### `initMap()`
Inicializa o mapa Leaflet, adiciona tiles OSM, cria o pane `brasilPane` (z-index 210) com o overlay GeoJSON do Brasil, e configura a centralização de popup ao clicar.

#### `carregarFiltros()`
Busca `GET /indicadores/api/mapa/filtros/` e popula todos os selects. Após popular o select de UF, armazena todas as opções em `allUfOptions` para uso no filtro cascata de Região → Estado.

#### `carregarDados()`
Busca `GET /indicadores/api/mapa/dados/` e armazena os features em `allFeatures`. Chama `filtrar()` ao concluir.

#### `filtrar()`
Aplica todos os filtros ativos sobre `allFeatures`, limpa `markerLayer` e recria os marcadores filtrados. Atualiza o painel de totais (valor somado e contagem de municípios).

#### `_radiusByPorte(porte) → number`
Retorna o raio do marcador em pixels com base no porte populacional:
- Capital → 20px
- Acima de 80mil → 13px
- Abaixo de 80mil → 7px
- (vazio) → 6px

#### `buildPopup(props) → string`
Monta o HTML do popup com os dados do município: nome, UF, porte, região, eixos de financiamento e valor estimado 2023–2030.

#### `buildLegend()`
Monta a legenda lateral com os eixos/programas disponíveis e seus colores. Exibe ou oculta o item "Sem financiamento" conforme o toggle.

#### `atualizarEstadosPorRegiao(regiao)`
Filtro cascata: reconstrói o select `#mg-f-uf` exibindo apenas os estados da região informada. Recebe `""` para restaurar todos os estados. Mantém o valor selecionado se o estado ainda pertencer à nova região.

#### `limparFiltros()`
Reseta todos os selects para o valor padrão (`""`), restaura todos os estados via `atualizarEstadosPorRegiao("")`, limpa o campo de município e chama `filtrar()`.

#### `baixarDados()`
Exporta os features filtrados como CSV com BOM UTF-8 (compatível com Excel). Colunas: município, UF, região, porte, eixo, valor.

#### `imprimirMapa()`
Usa `html2canvas` para capturar o elemento `#mg-map` e abre a imagem em nova aba para impressão.

---

### Fluxo de dados

```
DOMContentLoaded
  ├─ initMap()              inicializa Leaflet + overlay Brasil
  ├─ carregarFiltros()      GET /api/mapa/filtros/ → popula selects + allUfOptions
  └─ carregarDados()        GET /api/mapa/dados/   → allFeatures → filtrar()

Ao mudar qualquer filtro (exceto Região) → filtrar()
Ao mudar #mg-f-regiao → atualizarEstadosPorRegiao() → filtrar()
Ao digitar município → debounce 300ms → filtrar()
"Limpar filtros" → limparFiltros() → filtrar()
"Baixar dados"   → baixarDados()
"Print Mapa"     → imprimirMapa()
```

---

### Filtros disponíveis

| ID do elemento | Filtro | Tipo |
|---|---|---|
| `#mg-f-eixo` | Financiamento (eixo/programa) | Select simples |
| `#mg-f-modalidade` | Modalidade | Select simples |
| `#mg-f-estagio` | Estágio | Select simples |
| `#mg-f-executor` | Executor | Select simples |
| `#mg-f-regiao` | Região | Select simples (controla cascata do Estado) |
| `#mg-f-uf` | Estado (UF) | Select simples (cascata: depende de Região) |
| `#mg-f-porte` | Porte Populacional | Select fixo (Capital / Acima de 80mil / Abaixo de 80mil) |
| `#mg-f-municipio` | Município | Input texto livre |
| `#mg-f-sem-financiamento` | Exibir sem financiamento | Toggle (checkbox) |

---

## Estrutura HTML resumida

```
.mg-page
├── .mg-intro              (título + descrição)
└── .mg-layout
    ├── .mg-sidebar
    │   ├── .mg-sidebar-header  ("Filtros")
    │   ├── .mg-filters
    │   │   ├── #mg-f-eixo          (Financiamento)
    │   │   ├── #mg-f-modalidade    (Modalidade)
    │   │   ├── #mg-f-estagio       (Estágio)
    │   │   ├── #mg-f-executor      (Executor)
    │   │   ├── #mg-f-regiao        (Região)
    │   │   ├── #mg-f-uf            (Estado — cascata)
    │   │   ├── #mg-f-porte         (Porte Populacional)
    │   │   ├── #mg-f-municipio     (Município — texto livre)
    │   │   └── #mg-f-sem-financiamento  (toggle)
    │   └── .mg-sidebar-actions
    │       ├── #mg-btn-limpar    (Limpar filtros)
    │       ├── #mg-btn-baixar    (Baixar dados CSV)
    │       └── #mg-btn-print     (Print Mapa)
    └── .mg-map-area
        ├── #mg-loader             (spinner durante carregamento)
        ├── #mg-map                (instância Leaflet)
        ├── .mg-stats-panel        (Total Estimado 2023 a 2030 + contagem municípios)
        └── .mg-legend             (legenda: programa/eixo + sem financiamento)
```

---

## Estilos notáveis (`mapa-georreferenciado.css`)

| Seletor | Descrição |
|---|---|
| `body.mapa-page .rb-main` | Remove padding/background do layout base |
| `.mg-layout` | Grid: sidebar 280px + área do mapa `1fr` |
| `.mg-map-area` | `position: relative` para sobreposição correta do painel de stats e legenda |
| `#mg-map` | `position: absolute; inset: 0` — ocupa todo o `mg-map-area` |
| `.mg-stats-panel` | Sobreposição no canto superior direito do mapa com totais |
| `.mg-legend` | Sobreposição no canto inferior esquerdo com programa/cor |
| `.mg-toggle-row` | Toggle switch estilizado para "Exibir sem financiamento" |
