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

### Paleta de Cores

| Token                      | Valor        | Uso                                          |
|----------------------------|--------------|----------------------------------------------|
| `--color-header-bg`        | `#1B3333`    | Header, footer wave                          |
| `--color-primary`          | `#2c6174`    | Botões, bordas ativas, ícones                |
| `--color-primary-dark`     | `#1a3d4d`    | Textos de destaque, cabeçalhos de painel     |
| `--color-primary-mid`      | `#356073`    | Gradientes intermediários                    |
| `--color-primary-grad-start`| `#1e424f`   | Início dos gradientes de painel              |
| `--color-bg-page`          | `#bdd6e0`    | Fundo geral de todas as páginas              |

**Gradientes principais:**

```css
--gradient-panel-header: linear-gradient(135deg, #1e424f 0%, #2c6174 55%, #356073 100%);
--gradient-btn-primary:  linear-gradient(135deg, #1e424f 0%, #2c6174 60%, #356073 100%);
--gradient-landing:      linear-gradient(135deg, #264a57 0%, #356073 60%, #3d6e85 100%);
```

### Histórico da Paleta

- **Fase inicial:** Header com textura de imagem (`bg-header.png`) e gradiente escuro.
- **Commit `f4649e0`:** Removidas texturas. Cor sólida `#1B3333` no header e rodapé. Fundo da página migra para `#bdd6e0` (azul-claro).
- **Commit `9ac604a`:** Toda a paleta encapsulada em `static/css/tokens.css` como CSS custom properties. `base.css` passa a consumir variáveis em vez de valores hardcoded.

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

- Onda SVG decorativa no topo (fill `var(--color-bg-page)`)
- 3 colunas: Contato | Copyright | Siga-nos + logos parceiros
- Logos parceiros (C40, GCOM, FNP): `height: 44px`, `filter: brightness(0) invert(1)`, `opacity: 0.75`
  - *Revisão `5380679`:* reduzido de 72px → 44px para melhor harmonia
- Ícones de redes sociais: Instagram, LinkedIn, X, YouTube

### Favicon

Adicionado no commit `d82d7b6`:
```html
<link rel="icon" type="image/svg+xml" href="{% static 'img/logo-radar.svg' %}">
<link rel="apple-touch-icon" href="{% static 'img/logo-radar.svg' %}">
```

---

## 5. Páginas — Design Detalhado

### 5.1 Landing Page (`/`)

**Arquivo CSS:** `landing.css`

**Layout:** 2 colunas — sidebar (240px) + coluna de cards

**Sidebar:**
- Card hero: gradiente `--gradient-landing`, borda glass, hover com translateY(-2px)
- Cards laterais (Notícias, Agenda): glassmorphism leve `rgba(255,255,255,.72)`, blur 18px

**Cards de conteúdo:**
- Glassmorphism: `rgba(255,255,255,.72)`, blur 22px, saturate 1.3
- Grid interno: imagem thumbnail 120px + texto
- Thumbnail com `background: #fff` e `object-fit: contain`
- Numeração: `DM Mono`, 10px, `rgba(53,96,115,.5)`
- Título: `Sora 700`, 15.5px, `#1a2e3a` com `em` em `#356073`

**Botão "Saiba mais":**
- Ativo: gradiente `--gradient-landing`
- Card 4 (Ecossistema, em breve): `<span aria-disabled="true">` com classe `.lp-btn-card--soon` — fundo muted + badge "Em breve"

**Imagens:** `loading="lazy"` em todos os thumbnails e imagens de agenda

### 5.2 Início (`/inicio/`)

**Arquivo CSS:** `inicio.css`

Cards de acesso rápido redirecionam para aba correta do Painel Multinível via `?aba=N`.
Badge pulsante verde nas seções Início e Metodologia (`6f1eb79`).

### 5.3 Metodologia (`/metodologia/`)

**Arquivo CSS:** `metodologia.css`

- Hero zone com imagem de fundo (`bg-body.png`)
- Cards de seção com glassmorphism
- Redesenhada no commit `091f596` com glassmorphism e hero zone

### 5.4 Painel Multinível (`/indicadores/painel-multinivel/`)

**Arquivo CSS:** `painel-multinivel.css`

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

---

## Regra de Atualização

Sempre que uma alteração de design for feita — seja CSS, HTML estrutural, comportamento visual em JS ou novo componente — registrar neste arquivo:

1. Adicionar linha na tabela do [Histórico de Alterações](#9-histórico-de-alterações)
2. Atualizar a seção correspondente (página, componente ou design system)
3. Se for um novo token ou componente, adicionar nas tabelas das seções 3 ou 4
4. Commitar o `design.md` junto com as alterações de código
