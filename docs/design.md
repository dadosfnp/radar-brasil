# Design — Radar Brasil

Documentação completa de todas as decisões e evoluções de design da plataforma.
**Regra:** qualquer alteração visual, de componente ou de UX deve ser registrada neste arquivo antes do commit.

---

## Sumário

1. [Identidade Visual](#1-identidade-visual)
2. [Tipografia](#2-tipografia)
3. [Design System](#3-design-system)
4. [Componentes Globais](#4-componentes-globais)
5. [Páginas — Design Detalhado](#5-páginas--design-detalhado)
6. [Responsividade Mobile](#6-responsividade-mobile)
7. [Acessibilidade](#7-acessibilidade)
8. [Melhorias de UX/UI](#8-melhorias-de-uxui)
9. [Histórico de Alterações](#9-histórico-de-alterações)

---

## 1. Identidade Visual

### Paleta de Cores — versão atual (2026-08-17)

Nova identidade visual desenvolvida pelo time de comunicação da FNP. Paleta navy/azul substitui toda a paleta teal/verde anterior.

| Token                       | Valor        | Uso                                              |
|-----------------------------|--------------|--------------------------------------------------|
| `--color-header-bg`         | `#101d4f`    | Header principal e rodapé                        |
| `--color-primary`           | `#264584`    | Azul de referência: botões, barras, ícones       |
| `--color-primary-dark`      | `#1a3468`    | Hover escuro sobre primary                       |
| `--color-primary-deep`      | `#101d4f`    | Títulos e headings                               |
| `--color-primary-light`     | `#3b6cbf`    | Hover suave                                      |
| `--color-bg-page`           | `#d9e8f5`    | Fundo geral de todas as páginas (azul claro)     |
| `--color-text-primary`      | `#101d4f`    | Texto principal                                  |
| `--color-text-muted`        | `#5577aa`    | Texto secundário/muted                           |

**Regra de degradês:** Nenhum `linear-gradient` com cores da marca. Os tokens `--gradient-panel-header`, `--gradient-btn-primary` e `--gradient-landing` valem `#264584` (cor sólida).

**Exceção:** Bolinhas piscantes "METODOLOGIA" e "FEDERALISMO CLIMÁTICO" mantidas em `#22c55e` (verde claro — decisão estética aprovada).

**Logos disponíveis (`static/img/`):**

| Arquivo | Contexto de uso |
|---|---|
| `logo-radar-fundo-escuro.svg` | Header (fundo navy) |
| `logo-radar-fundo-claro.svg` | Backgrounds claros |
| `logo-radar-negativo-monocromatico.svg` | Impressão / fundo branco |
| `logo-radar-positivo-monocromatico.svg` | Fundo escuro monocromático |
| `avatar-principal.svg` | Favicon / ícone de app |
| `avatar-positivo.svg` | Variante positiva do avatar |
| `avatar-negativo.svg` | Variante negativa do avatar |

### Histórico da Paleta

- **Fase inicial:** Header com textura de imagem (`bg-header.png`) e gradiente escuro.
- **Commit `f4649e0`:** Removidas texturas. Cor sólida `#1B3333` no header e rodapé. Fundo da página migra para `#bdd6e0`.
- **Commit `9ac604a`:** Toda a paleta encapsulada em `static/css/tokens.css` como CSS custom properties.
- **2026-08-17:** Nova identidade visual — paleta teal/verde substituída por navy/azul `#264584`. Fundo `#bdd6e0` → `#d9e8f5`. Logos e avatares atualizados.

---

## 2. Tipografia

| Fonte           | Pesos       | Uso principal                                              |
|-----------------|-------------|------------------------------------------------------------|
| **Roboto**      | 300/400/500/700 | Corpo de texto, tabelas, selects, descrições           |
| **Sora**        | 400/600/700 | Títulos de cards, labels de KPI, abas, botões de destaque  |
| **DM Sans**     | 400/500/600 | Landing page — corpo e títulos secundários                 |
| **DM Mono**     | 500         | Numeração dos cards da landing (`01 — Painéis`)            |

Carregadas via Google Fonts no `<head>` do `base.html`.

### Escala de tamanhos (tokens)

```css
--text-xs:   0.625rem    /* 10px  — labels uppercase, badges */
--text-sm:   0.6875rem   /* 11px  — sublabels, eyebrows      */
--text-base: 0.875rem    /* 14px  — corpo padrão             */
```

---

## 3. Design System

### Arquitetura de arquivos CSS

```
static/css/
├── tokens.css       ← fonte da verdade: cores, gradientes, sombras, raios, transições
├── components.css   ← classes reutilizáveis entre páginas (cards, botões, headers, utilitários)
├── base.css         ← layout global: header, nav, footer, main container
└── [página].css     ← estilos exclusivos de cada página
```

**Ordem de carregamento** (base.html):
`tokens.css` → `components.css` → `base.css` → CSS de página

### tokens.css — variáveis globais

Criado no commit `9ac604a`. Centraliza todos os design tokens:

```css
:root {
  /* Cores */
  --color-header-bg:          #1B3333;
  --color-primary:            #2c6174;
  --color-primary-dark:       #1a3d4d;
  --color-primary-mid:        #356073;
  --color-primary-grad-start: #1e424f;
  --color-bg-page:            #bdd6e0;

  /* Gradientes */
  --gradient-panel-header: linear-gradient(135deg, var(--color-primary-grad-start) 0%, var(--color-primary) 55%, var(--color-primary-mid) 100%);
  --gradient-btn-primary:  linear-gradient(135deg, var(--color-primary-grad-start) 0%, var(--color-primary) 60%, var(--color-primary-mid) 100%);
  --gradient-landing:      linear-gradient(135deg, #264a57 0%, var(--color-primary-mid) 60%, #3d6e85 100%);

  /* Sombras */
  --shadow-glass: 0 8px 40px rgba(10,45,41,.12), 0 1px 4px rgba(10,45,41,.06);
  --shadow-card:  0 6px 32px rgba(10,45,41,.11), 0 1px 4px rgba(10,45,41,.06);

  /* Border radius */
  --radius-3xl: 20px;
  --radius-xl:  14px;
  --radius-lg:  10px;
  --radius-md:  8px;

  /* Transições */
  --transition-fast: .15s;
  --transition-base: .20s;
  --transition-slow: .30s;
}
```

### components.css — componentes compartilhados

Criado no commit `9ac604a`. Usa **multi-seletores** para eliminar CSS duplicado sem alterar HTML:

```css
/* Card glassmorphism */
.rb-card-glass, .pm-panel-card, .ap-card { ... }

/* Cabeçalho de painel com gradiente */
.rb-panel-header, .pm-card-header, .ap-card-header { ... }

/* Botão gradiente primário */
.rb-btn-gradient, .pm-criteria-badge, .ap-ficha-btn { ... }
```

**Componentes utilitários disponíveis:**

| Classe               | Descrição                                                  |
|----------------------|------------------------------------------------------------|
| `.rb-card-glass`     | Card glassmorphism (blur 26px + saturate 1.3)              |
| `.rb-card`           | Card sólido sem glassmorphism                              |
| `.rb-panel-header`   | Header de painel com gradiente                             |
| `.rb-btn-gradient`   | Botão gradiente primário com shimmer                       |
| `.rb-btn-solid`      | Botão sólido                                               |
| `.rb-btn-outline`    | Botão outline                                              |
| `.rb-select-wrap`    | Wrapper de `<select>` com seta customizada                 |
| `.rb-loader`         | Spinner SVG animado                                        |
| `.rb-empty-state`    | Estado vazio com ícone + título + descrição                |
| `.rb-page-intro`     | Cabeçalho de seção com `h2` + `p` padronizados             |
| `.rb-scroll-top`     | Botão flutuante voltar ao topo (oculto em páginas de mapa) |
| `.pm-chart-error`    | Overlay de erro sobre área de gráfico                      |

---

## 4. Componentes Globais

### Header

**Arquivo:** `static/css/base.css` — `.rb-header-wrapper`, `.rb-header`

- Fundo: `var(--color-header-bg)` — `#1B3333`
- Layout 3 colunas: `[logo-radar] [título + subtítulo] [logo-FNP]`
- Logo Radar Brasil (SVG) à esquerda com link para home
- Logo FNP à direita com link externo para fnp.org.br
- `box-shadow` inferior suave

**Evolução:**
- Fase inicial: textura de imagem no fundo
- Commit `dc69471`: reorganização 3 colunas, logos harmonizados
- Commit `f54ef12`: logo Radar Brasil adicionado à esquerda
- Commit `f4649e0`: textura removida, cor sólida `#1B3333`

### Barra de Navegação

**Arquivo:** `base.css` — `.rb-main-nav`

- Fundo branco com sombra sutil
- Links com `active` state: cor primary + underline
- Hamburger menu em mobile (≤768px): `≡` → `×`

### Footer

**Arquivo:** `base.css` — `.rb-footer-landing`

- 3 colunas: Contato | Copyright | Siga-nos + logos parceiros
- Logos parceiros (C40, GCOM, FNP): `height: 44px`, `filter: brightness(0) invert(1)`, `opacity: 0.75`
- Icones de redes sociais: Instagram, LinkedIn, X, YouTube

**Onda de transicao (`.rb-footer-wave`) — atualizado 2026-09-01:**
- Posicionada FORA do `<footer>`, como elemento irmaoo antes dele no DOM
- SVG invertido: `fill="#101d4f"` (navy, mesma cor do footer) preenche a area inferior com borda curva; area superior e transparente, mostrando o background da pagina naturalmente
- Path: `M0,60 C360,100 1080,100 1440,60 L1440,100 L0,100 Z`
- Funciona para todas as paginas sem override por pagina: em paginas com `fundo-bg.png` a curva revela o fundo-bg; em paginas brancas revela o `#ffffff` do body
- Elimina a faixa colorida (strip) que aparecia entre o conteudo e o rodape

**Background global (html) — atualizado 2026-09-01:**
- `html { background: url('../img/fundo-bg.png') center top / cover no-repeat fixed }` — cobre 100% do viewport com a imagem de ondas
- `body.rb-body { background: transparent }` — body transparente herda o fundo do html em paginas internas
- Paginas brancas (Landing, Inicio, Metodologia): `body { background: #ffffff }` cobre o html; `fundo-bg.png` aparece apenas no hero
- Paginas internas: fundo-bg.png visiivel em toda a pagina (substitui o antigo azul solido)

### Favicon

Adicionado no commit `d82d7b6`:
```html
<link rel="icon" type="image/svg+xml" href="{% static 'img/logo-radar.svg' %}">
<link rel="apple-touch-icon" href="{% static 'img/logo-radar.svg' %}">
```

---

## 5. Páginas — Design Detalhado

### 5.1 Landing Page (`/`)

**Arquivo CSS:** `landing.css` — versao atual: v8 (2026-09-01)

#### v8 — Ajustes de conteudo e background (2026-09-01)

- Hero com `fundo-bg.png` (substituindo cor solida `#cde3f4`)
- Subtitulo simplificado: "Impulsionando Acao Climatica e Federativa" (removido "com Dados Abertos")
- `body.lp-body { background: #ffffff }` — secao de conteudo branca

#### v6/v7 — Redesign completo com hero animado (2026-08-27)

**Arquivo CSS:** `landing.css` — versao historica: v6 (2026-08-27)

#### v6 — Redesign completo com hero animado (2026-08-27)

**Hero (full-width, fora do container .rb-main):**
- Fundo: `#cde3f4` (azul claro)
- `::before` / `::after` com fade-out para `#d9e8f5` (cor da página) — z-index 0, atrás do conteúdo
- Grid 44% / 56%: coluna esquerda (texto + CTAs + métricas) / coluna direita (mapa HUD)
- Coluna esquerda: eyebrow DM Mono uppercase → heading Sora 68px 800 `#101d4f` → subtítulo com span `.lp-hero-accent` azul `#2563eb` → desc `opacity:.72` → CTAs (navy pill sólido + outline pill) → métricas (+5 / +1.000 / 100%)
- Coluna direita: `<iframe src="mapa-brasil-hud.html" allowtransparency="true">` com `mask-image` suavizando bordas (transparent→black 7%→black 78%→transparent)
- Info card glassmorphism (`rgba(255,255,255,.86)`, blur 16px): `position:absolute; top:20px; right:20px` dentro de `.lp-hero-right`
- `mapa-brasil-hud.html`: `html,body { background: transparent }` para iframe transparente

**Seção de conteúdo (`.lp-content`, max-width 1140px):**
- Grid 2 colunas: sidebar 252px + painéis flex-1
- Sidebar: card "Sobre o Radar Brasil" + card "Navegue Rápido" + card feature com `radar_brasil_brasilia_alta_qualidade.png` e overlay "Dados abertos, sociedades mais resilientes."
- Cabeçalho da seção de painéis: eyebrow "Nossos Painéis" + heading "Explore conhecimento que gera soluções" + link "Ver todos os painéis →"

**Cards de painéis (vertical):**
- Labels: 01 Panorama, 02 Análises, 03 Território, 04 Colaboração
- Topo: ícone Lucide (TrendingUp / BarChart2 / MapPin / Users) em quadrado 40×40 `rgba(37,99,235,.10)`, stroke `#2563eb` + número DM Mono + título Sora 700
- Corpo: descrição 12px
- Footer: botão navy pill sólido `#264584` + seta circular navy 34px

**Botões:**
- CTAs hero: pill `border-radius:50px` (primário navy sólido; secundário outline navy)
- Cards: botão navy pill + seta circular navy — sem variações de cor por card

**Responsivo:**
- `≤1100px`: hero colapsa para 1 coluna, coluna direita e info card ocultos
- `≤860px`: sidebar sobre painéis (1 coluna)
- `≤580px`: painéis em coluna única

#### v5 — Layout anterior (até 2026-08-26)

**Layout:** hero 2 colunas (texto + mapa card) + main 2 colunas (sidebar 268px + grid 2×2)
**Hero right:** card glassmorphism `rgba(255,255,255,.75)` com `card_mapa_interfederativo.png`
**Cards:** layout horizontal (ícone 72px esq + texto dir), botões outline coloridos por card, seta circular com `--gradient-landing`

### 5.2 Início (`/inicio/`)

**Arquivo CSS:** `inicio.css` — versao atual: v10 (2026-09-01)

#### v10 — Titulo reestruturado, info card removido (2026-09-01)

- Titulo do hero: 2 linhas ("Explore os eixos / do Radar Brasil") com `font-size: 2.5rem`, `line-height: 1.18`
- Nova classe `.ini-hero-cats`: linha de categorias abaixo do titulo ("Governanca · Politicas e Planos · Programas · Financiamento"), `font-size: 0.8125rem`, cor `#264584 opacity 0.75`
- Info card "Dados que Geram Impacto" removido do hero

#### v3/v9 — Hero full-width com HUD (2026-08-31)

**Redesign v3 (2026-08-31):**

Layout geral:
- `body.inicio-page .rb-main` com `max-width: none; padding: 0; margin: 0` para hero full-width
- Três seções: hero (`.ini-hero`) + grid de eixos (`.ini-content`) + banner inferior (`.ini-bottom-banner`)

Hero:
- Fundo `#daedf8`, altura mínima 480px, grid 46%/54%
- Coluna esquerda: badge pulsante verde "Federalismo Climático" + heading Sora 1.875rem + descrição DM Sans
- Coluna direita: iframe `mapa-brasil-hud.html` com `mask-image` suavizando bordas + info card glassmorphism posicionado no canto inferior direito
- Info card: `rgba(255,255,255,0.82)` + `backdrop-filter: blur(14px)` + chips "Painéis / Mapas / Dados"

Cards (grid 2×2, `max-width: 1080px`):
- Layout horizontal: ícone 72×72px (fundo `rgba(38,69,132,.08)`) + corpo (eyebrow caps + título bold + desc + "Saiba mais →") + seta circular
- Fundo da seção: `fundo-bg.png` (cover) — imagem de ondas
- Hover: `translateY(-4px)`, seta circular muda para fundo navy sólido `#264584`

Banner inferior:
- Faixa navy `#264584`, padding 16px 40px, dois textos uppercase em `rgba(255,255,255,0.80)`

Versão anterior (v2): 2×2 grid de cards com cabeçalho navy horizontal, ícone centralizado acima, layout vertical. Sem hero.

### 5.3 Metodologia (`/metodologia/`)

**Arquivo CSS:** `metodologia.css` — v23 (2026-09-04)

- Hero zone com imagem de fundo (`bg-body.png`)
- Cards de seção com glassmorphism
- Redesenhada no commit `091f596` com glassmorphism e hero zone

**Carousel (v23 — 2026-09-04):**
- Texto atualizado para versão oficial da Resolução N°3: "O propósito do Federalismo Climático é de buscar..."
- Adicionada linha de atribuição abaixo do quote: `.meto-carousel-source` — `0.71875rem`, `rgba(255,255,255,.52)`, `letter-spacing: .03em`
- Quote usa aspas tipográficas HTML (`&#8220;` / `&#8221;`) em vez de aspas simples

**Timeline (v24 — 2026-09-04, revert fundo + EN i18n):**
- Fundo da seção revertido para `#fff` (gradient navy havia sido adicionado sem solicitação)
- Override `color: #ffffff` do heading removido
- Linha horizontal (`::before`): `rgba(38,69,132,.20)`, 2px espessura
- Conector vertical: `rgba(38,69,132,.25)` (navy translúcido)
- Scrollbar thumb: `rgba(38,69,132,.25)` (navy translúcido)
- Bolha circular 56×56px navy `#264584` mantida (substituiu pill amarela `#f5c400`)
- i18n: 18 strings da seção de cálculo traduzidas para EN

**Header Global — remoção de ::before (base.css v12):**
- Removido bloco `.rb-header-wrapper::before { top: -10px; height: 10px }` que causava faixa branca acima do header sticky

**Timeline (v23 — 2026-09-04, redesign navy):**
- Seção: fundo gradient navy `linear-gradient(160deg, #101d4f 0%, #264584 100%)` substituindo branco
- Heading da seção: `color: #ffffff`
- Bolha do ano: círculo 56×56px (`border-radius: 50%`), background `#264584`, texto `#ffffff`, borda branca translúcida, glow `rgba(255,255,255,.18)` — elimina a pill amarela `#f5c400` fora da paleta
- Linha horizontal (`::before`): `rgba(255,255,255,.20)`, 3px espessura, `bottom: 46px`
- Conector vertical: `rgba(255,255,255,.25)` (era navy translúcido)
- Scrollbar thumb: `rgba(255,255,255,.25)` (era navy translúcido)
- Cards: mantidos com fundo `#f5f8ff` (leitura clara sobre fundo navy)

**Timeline (v22 — 2026-09-04):**
- Layout invertido: cards agora alinhados pelo TOPO, linha horizontal movida para a BASE
- Conectores verticais flexíveis (`flex: 1`) preenchem o espaço entre o card e o dot
- `align-items: stretch` no track garante todos os eventos com mesma altura
- CSS `order` posiciona card(1) → conector(2) → dot(3) no DOM sem alterar HTML
- Mobile: bolhas com `order: 1` voltam para esquerda do layout horizontal

**Seção Metodologia de Cálculo (v22 — 2026-09-04, nova seção):**
- Nova seção final com 3 cards: Nível Parcial, Nível Eixo, Nível País
- Cada card: número de etapa circular + título/subtítulo + fórmula matemática em fração + texto descritivo + tabela de referência
- Nível País: fundo gradient navy `#101d4f → #264584`, step amarelo, texto e tabela em branco translúcido
- Fórmulas em fonte monospace (DM Mono), fração CSS (flex column)
- Grid 3 colunas desktop, 1 coluna mobile (`<=900px`)
- Fundo da seção: `#f0f4fb` (azul muito claro, contraste sutil com branco das cards)

### 5.4 Painel Multinível (`/indicadores/painel-multinivel/`)

**Arquivo CSS:** `painel-multinivel.css` — v13 (2026-09-04)

**Waffle chart (v14 — 2026-09-04):**
- Célula: 22px → 20px; gap: 4px → 3px — 31 células (Governança) cabem nos 752px disponíveis sem scroll
- Total 31 células: `31×20 + 30×3 = 710px` < 752px disponíveis

**Waffle chart (v13 — 2026-09-04):**
- `.pm-grid-cells`: `overflow: hidden` -> `overflow-x: auto` com scrollbar 2px (thin)
- Sincronização de scroll: `scroll` event listener em todas as `.pm-grid-cells` propaga `scrollLeft`
- Régua de tick marks: linha extra `.pm-grid-ruler-row` abaixo do waffle, com spans `.pm-grid-tick` a cada posição e `.pm-grid-tick--label` a cada múltiplo de 5
- Ticks: altura 10px, borda-left azul translúcida; labels: negrito, borda mais opaca, numeral tabular
- CSS: ticks sem hover (override `transform: none; box-shadow: none`)

**KPI Strip:** 3 cards glassmorphism em grid 3 colunas
- Valor: `Sora 700`, 1.75rem, `--color-primary-dark`
- Tooltips nativos (`title=""`) em cada valor KPI (adicionado em `f4682bb`)

**Tab Bar (`.pm-card-header`):** gradiente `--gradient-panel-header`
- Abas inativas: `rgba(194,237,231,.60)`, ícone `opacity: 0.88`
- Aba ativa: fundo `rgba(255,255,255,.96)`, cor `--color-primary-dark`, sombra superior
- Pseudo-elemento `::after` cobre o border-bottom do header
- Navegação por teclado: ArrowLeft/ArrowRight/Home/End (adicionado em `f4682bb`)

**Área do gráfico:** Chart.js horizontal bar stacked
- Overlay de erro `.pm-chart-error` sem destruir o canvas (adicionado em `f4682bb`)

### 5.5 Avaliação Painel Multinível (`/indicadores/avaliacao-painel/`)

**Arquivo CSS:** `avaliacao-painel.css`

**Tab Bar:** mesma estrutura que Painel Multinível; ícone inativo `opacity: 0.88`

**Filtros em cascata:** Setor → Estrutura (grid 2 colunas)

**Filtros com Combobox (commit `4366baf`):**

- Substituídos `<select>`/`<datalist>` por componente `Combobox` JS customizado
- Campos: Instância de Governança (primeiro) → Setor (segundo)
- Preenchimento bidirecional: selecionar Instância → Setor preenchido automaticamente; selecionar Setor → filtra Instâncias
- Dropdown com `role="listbox"` / `role="option"`, busca por digitação com `<mark>` no trecho digitado
- Botão `×` de limpar + chevron toggle + navegação ArrowUp/Down/Enter/Escape

**Empty State (`#ap-placeholder`):**
- Ícone SVG clipboard (44px, `opacity: 0.30`)
- Texto em `<span id="ap-placeholder-text">` (itálico, `#6a8fa0`)
- Estado de erro `.ap-placeholder--error`: ícone vermelho + texto em `#b03030`
- Adicionado no commit `f4682bb`

**Modal Ficha Técnica:**
- Overlay fullscreen com `backdrop-filter`
- Trap de foco (Tab/Shift+Tab + Escape)
- Botão PDF abre janela de impressão

### 5.6 Nota País (`/indicadores/nota-pais/`)

**Arquivo CSS:** `nota-pais.css`

- Mapa mundi com Leaflet, marcadores por país signatário da CHAMP
- Sidebar de filtros (mesmo padrão do mapa georreferenciado)
- FAB mobile com bottom sheet
- KPI strip com grid 2×2 no mobile
- Scroll-to-top **oculto** nesta página (mapa full-screen)

### 5.7 Financiamento Climático (`/indicadores/financiamento-climatico/`)

**Arquivo CSS:** `financiamento-climatico.css`

**Filtros:** MultiSelect com checkboxes, search interno, dropdown inteligente (abre para cima se sem espaço)
- Mobile: `position: fixed` com backdrop

**Gráficos (Plotly):**
- Setor: barras verticais top 5 (cor `#2c7873`)
- Origem: barras horizontais com paleta multicor
- Ente Federativo: donut chart (hole 0.44)
- Fade suave (opacity 0.25 → 1) ao trocar filtros (adicionado em `f4682bb`)

**Tabela:** paginada (10 registros), exportação CSV

### 5.8 Mapa Georreferenciado (`/indicadores/mapa-georreferenciado/`)

**Arquivo CSS:** `mapa-georreferenciado.css`

**Layout:** sidebar (260px, fundo `#1a3d4d`) + área do mapa flex-1

**Marcadores Leaflet:**
- Verde `#4CAF50`: com financiamento
- Laranja `#F4511E`: sem financiamento (toggle)
- Raio por porte: Capital=20px, Acima 80k=11px, Abaixo 80k=5px
- Canvas renderer (evita bug de translate3d no html2canvas)

**Overlay do Brasil:** polígono simplificado `#1a4a2e`, `fillOpacity: 0.22`

**Painel de totais:** card branco `position: absolute` no canto superior direito

**Legenda:** card branco `position: absolute` no canto inferior direito
- Ícone de tamanho de círculo por porte

**FAB de filtros (mobile):**
- `position: absolute`, bottom-left, `border-radius: 50%`
- Oculto com `opacity: 0; pointer-events: none` quando sidebar aberta (`body.mg-sidebar-open`)

**Badge de filtros ativos:**
- `<span class="mg-filter-count-badge">` no botão "Limpar filtros"
- Fundo `rgba(255,255,255,.90)`, texto `#1a3d4d`, oculto quando count=0

**Sidebar mobile:** fecha imediatamente ao selecionar filtro (sem delay — era 350ms antes)

**localStorage:** filtros persistem entre reloads (`mg-filtros` key)

**Scroll-to-top:** oculto (mapa full-screen)

---

## 6. Responsividade Mobile

### Breakpoints

| Breakpoint | Contexto principal                                |
|------------|---------------------------------------------------|
| `≤ 900px`  | Sidebar do mapa → FAB + bottom sheet              |
| `≤ 860px`  | Landing page → 1 coluna                           |
| `≤ 768px`  | Hamburger nav, MultiSelect mobile fixed           |
| `≤ 600px`  | Charts Chart.js menores                           |
| `≤ 480px`  | Abas mobile: flex:1, ícone+label, padrão iOS      |

### Hamburger Menu

Ativo em `≤768px`. Botão `≡`/`×`, aria-expanded, fecha ao clicar em link.

**Redesenho (2026-09-03, base.css v6):**
- `.rb-nav-links` em mobile: `position: absolute; top: 100%; left: 0; right: 0` relativo ao `.rb-header-wrapper`
- Dropdown full-width imediatamente abaixo do header, background `#0d1640`, shadow profunda
- JS eleva `.rb-header-wrapper` para `z-index: 2300` ao abrir (acima dos sidebars de filtro z-index: 2100)
- Fecha ao clicar fora do header (`document.click` guard)

### Abas Mobile

Commit `f13438a` + `0cf9be1`:
- `flex: 1` — largura igual (padrão iOS/Android)
- Layout: ícone em cima + label abreviado (`data-short`)
- Label full: `font-size: 0` com `::after { content: attr(data-short); font-size: 0.59375rem }`

### Mapas Mobile

- Sidebar vira bottom sheet com FAB flutuante (commit `51ccb3e`)
- Altura: `100vh - 96px` (header ~46px + nav ~42px + buffer 8px) + `100svh` fallback
- FAB some quando sidebar aberta

### Footer Mobile

Redesenhado no commit `181ea3a`: 3 colunas → coluna única com logos alinhados.

### Tabela Financiamento Mobile

Commit `42e60f9`: layout de card (cada linha vira card com `data-label`).

### Melhorias Mobile UX/UI (2026-09-03 — base.css v7, metodologia.css v21, nota-pais.css v8, mapa-georreferenciado.css v6)

**PT/EN pill empilhado verticalmente no mobile (base.css v7):**
- Problema: `.rb-lang-form { position: absolute; bottom: -26px }` sobrepunha logo FNP no mobile
- Solucao: na media query 768px, `.rb-header-logo { flex-direction: column; align-items: flex-end; gap: 4px }` + `.rb-lang-form { position: static }`
- Pill passa a empilhar abaixo do logo FNP dentro do flex container; altura total ~60px (menor que o logo Radar 68px)

**Timeline Metodologia — layout vertical em mobile (metodologia.css v21):**
- Problema: timeline horizontal com scroll-x dificil de usar em telas pequenas
- Solucao em `≤600px`: scroll-x desativado, `.meto-timeline-track { flex-direction: column; gap: 16px }`, `.meto-tl-event { flex-direction: row; align-items: flex-start }`, `.meto-tl-year-bubble { position: static; min-width: 60px }`, `.meto-tl-connector { display: none }`, linha horizontal (`::before`) ocultada
- Resultado: cada evento como linha horizontal (bolha do ano | card)

**Mapas full-screen (Google Maps pattern) em mobile — (nota-pais.css v8, mapa-georreferenciado.css v6):**
- Problema: mapas a `65vh` em 900px eram pequenos demais; KPI strip empurrava mapa para cima
- Solucao: a partir de 900px, mapas passam a `height: calc(100svh - 88px)` (88px = header mobile)
- KPI strip fica abaixo do mapa, acessivel via scroll — mesmo padrao do Google Maps
- Tanto `.np-map-container` quanto `.mg-map-area` recebem a nova altura no breakpoint 900px

### Auditoria Mobile Completa (2026-09-03)

Correcoes aplicadas em 9 arquivos CSS (base.css v5, inicio.css v12, landing.css v11, avaliacao-painel.css v9, painel-multinivel.css v12, mapa-georreferenciado.css v5, financiamento-climatico.css v5, nota-pais.css v7):

**Bug critico — menu hamburger invisivel:**
- `.rb-nav-hamburger span`: `background: var(--hdr-700)` (#101d4f = mesmo tom do header) trocado por `rgba(255,255,255,0.85)`

**Touch targets (WCAG 2.1 AA — minimo 44px):**
- Todos os selects, inputs, botoes de acao, sidebar-close e FABs elevados para `min-height: 44px` ou `height: 44px`
- `.lp-panel-arrow`: 34px elevado para 44px
- `.fc-page-btn`: 28px elevado para 40px
- `.np-search-btn`: 32px elevado para 44px

**Textos legiveis (minimo ~11px em mobile):**
- `ini-card-eyebrow` (9px) e `ini-card-link` (11px) elevados para 12px
- 9 textos da landing abaixo de 11px corrigidos no breakpoint 580px
- `ap-niveis-atual-tag`: 8px elevado para 11px
- `fc-table tbody td::before`: 9.6px elevado para 11px
- `np-kpi-label`: 9px (900px) e 8.5px (480px) elevados para 11px e 10px

**Layout mobile:**
- `.pm-grid-row-label` em coluna: border-right / margin-right / text-align resetados
- `.pm-grid-cells`: `overflow: hidden` trocado por `overflow-x: auto` (scroll horizontal visivel)
- `.fc-table-wrap`: `overflow: hidden` trocado por `overflow-x: auto` (habilitado entre 769-1100px)
- `.mg-popup` em 320px: `min-width: 0; max-width: calc(100vw - 32px)`

---

## 7. Acessibilidade

Implementada no commit `55ef5ec` seguindo **WCAG 2.1 AA**.

### Medidas implementadas

| Área                  | Implementação                                                         |
|-----------------------|-----------------------------------------------------------------------|
| Skip link             | `<a href="#rb-main-content" class="rb-skip-link">` visível no foco    |
| Roles ARIA            | `role="tablist"`, `role="tab"`, `role="tabpanel"` nos painéis         |
| `aria-selected`       | Atualizado dinamicamente nas abas ao trocar eixo                      |
| `aria-controls`       | Tab → tabpanel vinculados por ID                                      |
| `aria-live="polite"`  | Área da tabela de avaliação notifica leitores de tela                 |
| `aria-labelledby`     | Tabpanel nomeado pelo tab ativo                                       |
| Navegação por teclado | ArrowLeft/Right/Home/End nos tabs (commit `f4682bb`)                  |
| Trap de foco          | Modal Ficha Técnica: Tab/Shift+Tab + Escape                           |
| `aria-hidden="true"`  | Todos os SVGs decorativos                                             |
| `alt=""` em ícones    | Ícones de tab com `alt=""` (decorativos)                              |
| `loading="lazy"`      | Imagens não críticas na landing page                                  |
| `role="status"`       | Loaders e placeholders                                                |
| Contraste             | Todos os textos principais ≥ 4.5:1 (AA)                               |

### SVG Loaders — padrão

`stroke-width="2"` para spinners de carregamento (normalizado em `f4682bb`).
Ícones informativos: `stroke-width="2.2"`.

---

## 8. Melhorias de UX/UI

Implementadas no commit `f4682bb` (sessão de auditoria completa, 23 itens):

### Alta Prioridade

| Item | Descrição | Arquivo(s) |
|------|-----------|------------|
| A1 | Tratamento de erros de API com feedback visual | `avaliacao-painel.js`, `painel-multinivel.js` |
| A2 | Navegação por teclado ArrowLeft/Right/Home/End nos tabs | `avaliacao-painel.js`, `painel-multinivel.js` |
| A3 | FAB some ao abrir sidebar no mobile | `mapa-georreferenciado.html`, `.css` |
| A4 | Remove delay de 350ms no fechamento da sidebar | `mapa-georreferenciado.html` |

### Média Prioridade

| Item | Descrição | Arquivo(s) |
|------|-----------|------------|
| B1 | Empty state com ícone SVG clipboard + texto estruturado | `avaliacao-painel.html`, `.css` |
| B2 | Badge contador de filtros ativos no botão "Limpar filtros" | `mapa-georreferenciado.html`, `.js`, `.css` |
| B3 | Normaliza `stroke-width="2"` em loaders SVG | `avaliacao-painel.html`, `painel-multinivel.html` |
| B4 | Botão scroll-to-top global (aparece após 400px) | `base.html`, `components.css` |
| B5 | Fade suave nos gráficos de financiamento ao trocar filtros | `financiamento-climatico.js` |
| B6 | Opacidade ícones de tab inativo: 0.72 → 0.88 | `avaliacao-painel.css`, `painel-multinivel.css` |

### Baixa Prioridade

| Item | Descrição | Arquivo(s) |
|------|-----------|------------|
| C1 | Componente `.rb-page-intro` padronizado | `components.css` |
| C2 | Componente `.rb-empty-state` padronizado | `components.css` |
| C3 | Persistência de filtros do mapa via localStorage | `mapa-georreferenciado.js` |
| C4 | Tooltips nativos (`title=""`) nos valores KPI | `painel-multinivel.html` |

### Polimento Profissional (commit `d82d7b6`)

- Meta tags Open Graph e Twitter Card
- Favicon SVG + apple-touch-icon
- Ano do copyright dinâmico: `{% now "Y" %}`
- Typo: "Inicio" → "Início"
- `scroll-behavior: smooth` no `html`
- `@media print` styles nos painéis
- `robots.txt` via Django TemplateView
- Card "Ecossistema" (em breve): link morto → `<span aria-disabled="true">` + badge

---

## 9. Histórico de Alterações

| Data       | Commit    | Descrição                                                       |
|------------|-----------|-----------------------------------------------------------------|
| 2026-04-14 | `9f16467` | Primeiro commit do projeto                                      |
| 2026-04-15 | `0184cea` | Layout inicial — página início, header e rodapé                 |
| 2026-04-24 | `9a7fa06` | Header e nav padronizados em todas as páginas                   |
| 2026-04-24 | `41c5600` | Painel Multinível com Chart.js                                  |
| 2026-05-04 | `091f596` | Redesign Metodologia com glassmorphism e hero zone              |
| 2026-05-05 | `b283ffa` | Página Avaliação Painel Multinível                               |
| 2026-05-07 | `03c178f` | Página Mapa Georreferenciado com Leaflet                        |
| 2026-05-12 | `788d560` | Página Financiamento Climático com gráficos e filtros           |
| 2026-05-12 | `d4dd9bd` | Página Nota País com mapa mundi                                 |
| 2026-05-14 | `b55d2a2` | Redesign visual global — glassmorphism                          |
| 2026-05-14 | `e0565ff` | Header/rodapé verde-escuro, menu branco, fundo `#bdd6e0`        |
| 2026-08-27 | —         | Landing Page v6: hero HUD animado, ícones Lucide, cards verticais |
| 2026-05-19 | `ab11c10` | Landing page vira página inicial (`/`)                          |
| 2026-05-20 | `33ae061` | Responsividade mobile completa + hamburger menu                 |
| 2026-05-20 | `0cf9be1` | Abas mobile: ícone + label abreviado (padrão iOS/Android)       |
| 2026-05-20 | `f13438a` | Abas mobile: flex:1 (largura igual)                             |
| 2026-05-20 | `51ccb3e` | Mapas: sidebar → FAB + bottom sheet no mobile                   |
| 2026-05-22 | `46cc5a5` | Design tokens iniciais em `base.css`                            |
| 2026-05-25 | `dc69471` | Header reorganizado 3 colunas, logos harmonizados               |
| 2026-05-25 | `f54ef12` | Logo Radar Brasil adicionado ao header (esquerda)               |
| 2026-05-28 | `f4649e0` | Remove texturas — cor sólida `#1B3333` + fundo `#bdd6e0`        |
| 2026-06-08 | `55ef5ec` | Acessibilidade WCAG 2.1 AA em toda a plataforma                 |
| 2026-06-09 | `d82d7b6` | Polimento profissional: meta tags, favicon, robots.txt, print   |
| 2026-06-10 | `4c53e08` | Remove apps e arquivos boilerplate sem uso                      |
| 2026-06-10 | `9ac604a` | Design system completo: `tokens.css` + `components.css`         |
| 2026-06-10 | `f4682bb` | 23 melhorias de UX/UI: erros, teclado, empty state, FAB, etc.   |
| 2026-06-10 | `5380679` | Logos parceiros no rodapé: `height` 72px → 44px                 |
| 2026-06-10 | `f8cb3e3` | Scroll-to-top oculto em páginas de mapa (conflito com legenda)  |
| 2026-07-02 | `4366baf` | Avaliação Painel: filtros substituídos por combobox customizado |
| 2026-07-02 | `09f10d6` | Rodapé: copyright em linha própria abaixo das colunas           |
| 2026-07-02 | `abd7175` | Rodapé: centralização do copyright corrigida (flex)             |
| 2026-07-03 | `bd6c8a5` | Avaliação Painel: texto de instrução do empty state atualizado  |
| 2026-07-13 | `011fa3c` | Popup do mapa: largura 290–320px para Perfil Investimento       |
| 2026-07-22 | (branch)  | i18n: seletor PT\|EN no header, `{% trans %}` na nav e subtítulo|
| 2026-07-22 | (branch)  | i18n full-coverage: 9 templates + 5 JS files, 236 strings EN    |
| 2026-07-22 | (branch)  | i18n fix: Avaliação Painel — eixo title, filter labels EN       |
| 2026-07-22 | (branch)  | i18n fix: varredura completa — 15 strings PT restantes corr.    |
| 2026-07-23 | (branch)  | ficha técnica: links clicáveis em nome, órgão e arcabouço       |
| 2026-07-23 | (branch)  | ficha técnica: cor dos links herda cor original do texto         |
| 2026-08-18 | `c2e87e4` | Filtros Financiamento: todos selecionados por default (remove defaultCount) |
| 2026-08-18 | `bbe5fbe` | Tabela mobile: layout empilhado, cabeçalho navy, repasses agrupados |
| 2026-08-24 | (pendente)| Página Início: redesign editorial — paleta papel+jade+barro, Fraunces/Public Sans/IBM Plex Mono, hero com indicadores, fichas de dossiê assimétrico, seção institucional |
| 2026-08-24 | (pendente)| Página Início: revert completo para estado `bbe5fbe` (2×2 glassmorphism, ícones SVG, cabeçalho navy) |
| 2026-08-24 | (pendente)| Ícones página Início: remove radial-gradient + inset shadow do `.ini-icon-wrap`; fundo flat `rgba(38,69,132,.08)` + borda |
| 2026-08-24 | (pendente)| Landing page: botão "Ver Agenda" → estado desabilitado `.lp-btn-side--soon` com badge "Em breve" |
| 2026-08-25 | (pendente)| Metodologia: hero single-column centrado, pills reordenadas, escala de avaliação movida para o fim da sidebar |
| 2026-08-25 | (pendente)| Metodologia: pip-4 corrigida — `#264584` → `#72be79` (verde Nível 4 do Painel Multinível) |
| 2026-08-25 | (pendente)| Financiamento: label filtro "Ente Federado" → "Nível de Governo" |
| 2026-08-25 | (pendente)| Layout global: `min-height: 70vh` → `0` em `.rb-main` (base.css, metodologia.css, mapa-georreferenciado.css) — footer visível sem scroll |
| 2026-08-25 | (pendente)| Footer wave: `height: 90px` → `50px` (desktop) e `50px` → `35px` (mobile) — reduz zona invisível da onda (mesma cor do fundo), tornando o dark navy visível quando scroll-to-top aparece |
| 2026-09-02 | pendente  | Header: nav integrada na barra azul (mesma linha dos logos); layout grid 3 colunas `auto 1fr auto`; header sticky; nav visível na landing |
| 2026-09-02 | pendente  | Header: logo Radar Brasil 124px, logo FNP 62px, alinhados pelo eixo central; pill PT/EN flutuante abaixo do logo FNP |
| 2026-09-02 | pendente  | Nav: links brancos `rgba(255,255,255,0.78)` no fundo navy; active com `border-bottom: 2px solid #fff`; fonte `1.051rem` |
| 2026-09-03 | pendente  | Nav: aba "Inicio" ocultada (`display:none`); "Painel Multinivel" → "Paineis"; "Avaliacao Painel Multinivel" → "Componentes" |
| 2026-09-03 | pendente  | Nivel 5 cor: azul #7aaed4/#A5C8ED substituido por verde escuro #27ae60 em todos os componentes (waffle, modal, badge, pip, escala) |
| 2026-09-03 | pendente  | Painel Multinivel waffle: largura do label fixada em 200px para alinhar celulas horizontalmente; flex-wrap nowrap + overflow hidden |
| 2026-09-03 | pendente  | Metodologia Escala de Avaliacao: adicionadas regras .meto-scale-pip.pip-N para exibir pips coloridos 1-5 |
| 2026-09-03 | pendente  | Metodologia v11: 6 secoes novas — piramide federalismo, carrossel 3 fotos, timeline horizontal, 4 cards definicao, 4 cards eixo/criterios, escopo + stats |
| 2026-09-03 | pendente  | Painel Multinivel: card "Explorar eixos" removido; KPI "Niveis de Maturidade" → "Niveis de Avaliacao"; KPI instancias dinamico por eixo |
| 2026-09-03 | pendente  | Metodologia: "Federalismo Climatico" corrigido para maiusculas em titulos e conceito box; "Como avaliamos" e "O que avaliamos" com bg branco |
| 2026-09-03 | pendente  | Avaliacao Painel: Nivel 5 com badge aprimorado (estrela, borda glow); descritivo completo no parametro; modal "Ver niveis" com escala 1-5 |
| 2026-09-03 | pendente  | Grafico Painel Multinivel: Chart.js bar substituido por grid heatmap — celulas coloridas por nivel, 1 linha por criterio, legenda compacta |
| 2026-09-02 | pendente  | Logos SVG do Radar Brasil atualizados (nova identidade visual); cards PNG do Inicio removidos; HUD atualizado |
| 2026-09-02 | pendente  | Texto "RADAR BRASIL / Impulsionando a Acao Climatica Federativa" removido do header |
| 2026-09-03 | pendente  | Refinamento visual senior: Escala de Avaliacao com barra gradiente; pips 40px uppercase; separador waffle label/celulas; acento lateral modal "Ver Niveis" |
| 2026-09-03 | pendente  | Metodologia cards definicao: icones redesenhados (layers/sliders/barras/grade), container 52px, SVG 26px, variante de cor sutil por card |
| 2026-09-03 | pendente  | Nivel 5: cor aprofundada para `#1a4a35` (verde floresta escuro) em todos os componentes — waffle, modal, badge, pip, escala, API |
| 2026-09-04 | (HEAD)    | i18n: auditoria EN completa — 86 strings novas em django.po (245→331); landing page totalmente traduzida em desktop e mobile |
| 2026-09-04 | (HEAD)    | fix mobile: modal Ver Niveis centralizado; badge Nivel 5 verde; Linha do Tempo sem clip; pill PT/EN lado a lado logo FNP; nav slimmer |
| 2026-09-04 | (HEAD)    | Header mobile: pill PT/EN removida do header; globo + PT/EN no fundo do dropdown hamburger (padrao C40 Cities); FNP logo 36px |

---

## Regra de Atualização

Sempre que uma alteração de design for feita — seja CSS, HTML estrutural, comportamento visual em JS ou novo componente — registrar neste arquivo:

1. Adicionar linha na tabela do [Histórico de Alterações](#9-histórico-de-alterações)
2. Atualizar a seção correspondente (página, componente ou design system)
3. Se for um novo token ou componente, adicionar nas tabelas das seções 3 ou 4
4. Commitar o `design.md` junto com as alterações de código
