# Nota País

Página do **Radar Brasil** que exibe um mapa-múndi interativo com os países signatários da **Coalizão CHAMP** e suas respectivas Nota-País — termômetro da capacidade de execução e cumprimento de compromissos climáticos.

---

## Arquivos envolvidos

| Caminho | Responsabilidade |
|---|---|
| `templates/municipios/nota-pais.html` | Estrutura HTML da página |
| `static/css/nota-pais.css` | Estilos exclusivos da página |
| `static/js/nota-pais.js` | Mapa Leaflet, dados, filtros e interações |
| `apps/indicadores/views.py` | View Django (`nota_pais_view`) |
| `apps/indicadores/urls.py` | Roteamento |

---

## Roteamento

| URL | View | Descrição |
|---|---|---|
| `/indicadores/nota-pais/` | `nota_pais_view` | Renderiza o template (sem API — dados embutidos no JS) |

A página não possui backend de dados: todos os conjuntos de dados (signatários, notas, cores, nomes em português) estão declarados como constantes no arquivo JS.

---

## Frontend (`nota-pais.js`)

### Constantes de dados

#### `CONTINENT_COLORS`
Paleta de cores por continente usada para colorir o mapa:
```
North America → #3EC9D4   South America → #4AB88A
Europe        → #4E80C5   Africa        → #E8943A
Asia          → #EFC040   Oceania       → #9870C8
Antarctica    → #C0D0D8
```

#### `ISO_CONTINENT`
Fallback de continente por código ISO A3 (≈ 130 países). Usado quando o GeoJSON não traz o campo `CONTINENT`.

#### `NOMES_PT`
Dicionário ISO A3 → nome do país em português. Usado nos labels do mapa e nos tooltips.

#### `CHAMP_SIGNATORIES`
`Set` com os códigos ISO A3 dos países signatários da Coalizão CHAMP (≈ 50 países). Apenas esses países recebem marcador de pino vermelho e label de nome.

#### `COUNTRY_NOTA`
Dicionário ISO A3 → string da nota. Atualmente apenas `BRA: "Nível 3,0"`. Países com nota recebem tooltip amarelo em destaque.

#### `OCEAN_LABELS`
Array com posições `[lat, lng]` e textos dos três oceanos (Pacífico, Atlântico, Índico), renderizados como marcadores de texto fixos.

#### `REGION_MAP`
Mapeia os valores do filtro de Regiões para os nomes de continente usados internamente:
```js
"americas" → ["North America", "South America"]
"europe"   → ["Europe"]
"africa"   → ["Africa"]
"asia"     → ["Asia"]
"oceania"  → ["Oceania"]
```

---

### Variáveis de estado (módulo)

| Variável | Tipo | Descrição |
|---|---|---|
| `map` | `L.Map` | Instância principal do Leaflet |
| `geoLayer` | `L.GeoJSON` | Camada GeoJSON dos países |
| `currentRegion` | `string` | Valor atual do filtro de região (`""` = todos) |
| `pinMarkers` | `Array<{marker, continent}>` | Marcadores de pino vermelho (CHAMP) |
| `labelMarkers` | `Array<{marker, continent}>` | Marcadores de nome dos países |

---

### Funções principais

#### `init()`
Executada no `DOMContentLoaded`. Cria o mapa, adiciona labels dos oceanos, busca o GeoJSON e registra os listeners:

- `#np-f-regiao` `change` → `applyRegionFilter(value)`
- `#np-btn-limpar` `click` → limpa todos os selects + chama `applyRegionFilter("")`
- `#np-btn-print` `click` → `window.print()`

#### `buildMap(data)`
Chamada após o GeoJSON ser carregado. Cria a `geoLayer` com:
- **Estilo por continente:** `CONTINENT_COLORS`
- **Tooltip hover:** exibe nome + nota (amarelo para Brasil, cinza para demais)
- **Mouseover/mouseout:** highlight temporário respeitando o filtro de região ativo

Itera sobre `data.features` e adiciona pinos vermelhos + labels de nome para cada signatário CHAMP encontrado, armazenando referências em `pinMarkers` e `labelMarkers`.

#### `applyRegionFilter(region)`
Aplica ou remove o filtro de região:
1. Atualiza `currentRegion`
2. Percorre `geoLayer.eachLayer()` e reestiliza cada país:
   - **Dentro da região:** cor original do continente, `fillOpacity: 0.84`
   - **Fora da região:** cinza `#C0C8C8`, `fillOpacity: 0.38`
3. Mostra/oculta cada item de `pinMarkers` e `labelMarkers` conforme o continente bate com a região

O `mouseout` de cada feature também respeita `currentRegion` ao restaurar a cor, evitando que o hover "limpe" a regra de filtro.

#### `addTextMarker(latlng, text, className) → L.Marker`
Cria um marcador não-interativo com ícone `L.divIcon` contendo um `<span>` com classes Leaflet de tooltip. Retorna o marcador (para que possa ser guardado nos arrays de estado).

#### Helpers

| Função | Descrição |
|---|---|
| `getIso(props)` | Extrai ISO A3 do feature (`ISO_A3`, `ADM0_A3`, `iso_a3`), retorna `""` para `-99` |
| `getName(props)` | Resolve nome em português via `NOMES_PT`, fallback para `NAME`/`ADMIN` |
| `getContinent(props)` | Lê `CONTINENT` do GeoJSON; fallback via `ISO_CONTINENT[iso]` |
| `getCentroid(feature)` | Calcula centróide do maior polígono (usado para posicionar pinos) |

---

## Fonte do GeoJSON

```
https://cdn.jsdelivr.net/gh/martynafford/natural-earth-geojson@master/110m/cultural/ne_110m_admin_0_countries.json
```

Natural Earth 110m — resolução baixa, adequada para mapa mundial. Carregado via `fetch` em cada visita (sem cache client-side).

Campos usados do GeoJSON: `ISO_A3`, `ADM0_A3`, `iso_a3`, `CONTINENT`, `continent`, `NAME`, `ADMIN`, `name`.

---

## Estrutura HTML resumida

```
.np-page
├── .np-intro                  (título + descrição)
├── .np-card
│   ├── .np-sidebar
│   │   ├── .np-sidebar-header ("ESCALA DA NOTA-PAÍS")
│   │   ├── .np-filters
│   │   │   ├── #np-f-pais           (Países Signatários)
│   │   │   ├── #np-f-compromisso    (Compromissos Climáticos)
│   │   │   ├── #np-f-iniciativa     (Iniciativas Ativas)
│   │   │   └── #np-f-regiao         (Regiões Monitoradas ← filtro ativo)
│   │   └── .np-actions
│   │       ├── #np-btn-limpar
│   │       ├── #np-btn-baixar
│   │       └── #np-btn-print
│   └── .np-map-container
│       └── #np-map                  (instância Leaflet)
└── .np-kpi-strip
    ├── 77 Países Signatários
    ├── +120 Compromissos Climáticos
    ├── 23 Iniciativas Ativas
    └── 5 Regiões Monitoradas
```

> Os KPIs são valores estáticos no HTML.
> Os selects de País, Compromisso e Iniciativa estão presentes na interface mas **ainda não possuem lógica de filtragem implementada** — apenas o filtro de Região está funcional.

---

## Estilos notáveis (`nota-pais.css`)

| Seletor | Descrição |
|---|---|
| `body.np-body .rb-main` | Remove padding/margin do layout base, ocupa 100% da altura |
| `.np-card` | Flex row: sidebar (260px fixo) + mapa (flex: 1) |
| `.np-map-container` | Fundo `#bdd8e8` (oceano), position relative |
| `#np-map` | `position: absolute; inset: 0` — preenche o container |
| `.leaflet-tooltip.np-tooltip` | Tooltip hover padrão (fundo escuro) |
| `.leaflet-tooltip.np-tooltip-brazil` | Tooltip especial amarelo para o Brasil |
| `.leaflet-tooltip.np-country-label` | Label de nome de país (transparente, texto pequeno) |
| `.leaflet-tooltip.np-ocean-label` | Label dos oceanos (itálico, azul semi-transparente) |
| `.np-kpi-strip` | Faixa de KPIs em flex row com separadores verticais |

**Nota importante sobre classes do body:** O `<body>` usa `class="rb-body np-body"` e o wrapper de conteúdo usa `class="np-page"`. Manter esses nomes separados evita que regras CSS do conteúdo (padding, gap) sejam aplicadas ao body.

---

## Dependências externas

| Biblioteca | Versão | Uso |
|---|---|---|
| Leaflet.js | 1.9.4 (CDN) | Mapa interativo |
| Leaflet CSS | 1.9.4 (CDN) | Estilos do mapa |
| Natural Earth GeoJSON | 110m (jsDelivr) | Geometrias dos países |
| Google Fonts — Sora | — | Tipografia dos títulos |
