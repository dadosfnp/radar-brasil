# CHANGELOG — Radar Brasil

Histórico cronológico de todas as alterações realizadas no projeto.

---

## 2026-07-13 — `011fa3c`

### Fix — Popup do mapa: largura ajustada para "Perfil Investimento" sem quebra de linha

- `.mg-popup` redimensionado de `250/290px` para `290/320px` — dimensão calculada para acomodar ícone (18px) + label "Perfil Investimento" (125px) + valor "Investimento Agrupado" (136px) + padding (28px) + respiro (6px)
- `bindPopup` com `minWidth: 320` e `maxWidth: 400` alinhados ao novo tamanho do card

**Arquivos:** `static/css/mapa-georreferenciado.css`, `static/js/mapa-georreferenciado.js`

---

## 2026-07-03 — `bd6c8a5`

### Fix — Texto de instrução na Avaliação Painel Multinível

- Atualizado texto de instrução do empty state para refletir o novo fluxo de filtros com combobox

**Arquivos:** `templates/municipios/avaliacao-painel.html`

---

## 2026-07-02 — `abd7175`

### Fix — Centralização do copyright no rodapé (ajuste flex)

- Corrigida centralização do `.rb-footer-copy` com `justify-content` no container flex

**Arquivos:** `static/css/base.css`

---

## 2026-07-02 — `09f10d6`

### Fix — Copyright do rodapé em linha própria abaixo das colunas

- `.rb-footer-col-center` substituído por `.rb-footer-bottom` — faixa de largura total abaixo das 3 colunas
- Texto de copyright: `font-size` 1rem → 0.9rem, `padding` ajustado para `8px 40px 18px`
- HTML do `base.html` atualizado com novo elemento `.rb-footer-bottom`

**Arquivos:** `base_templates/base.html`, `static/css/base.css`

---

## 2026-07-02 — `623a1da`

### Style — Formatação Black nos services

- Black aplicado em `avaliacao_painel.py` e `painel_multinivel.py` (sem mudança de comportamento)

**Arquivos:** `apps/indicadores/services/avaliacao_painel.py`, `apps/indicadores/services/painel_multinivel.py`

---

## 2026-07-02 — `4366baf`

### Feat — Filtros da Avaliação Painel com combobox customizado acessível

- Substituídos `<select>`/`<datalist>` por componente `Combobox` JS com dropdown acessível (`role="listbox"`, `role="option"`, `aria-expanded`, `aria-activedescendant`)
- Botão `×` (limpar) e chevron toggle em cada campo de filtro
- Busca por digitação com destaque (`<mark>`) do trecho digitado nas opções
- Navegação por teclado: ArrowUp/Down, Enter, Escape, Tab
- **Ordem dos campos invertida:** Instância de Governança aparece primeiro, Setor em segundo
- Preenchimento bidirecional: selecionar Instância → preenche Setor automaticamente; selecionar Setor → filtra Instâncias disponíveis
- Campo "Setor" adicionado como primeiro campo na Ficha Técnica do modal
- Label `LABEL_ESTRUTURA['Governanca']` atualizado para `'Instância de Governança'`

**Arquivos:** `apps/indicadores/services/avaliacao_painel.py`, `static/css/avaliacao-painel.css`, `static/js/avaliacao-painel.js`, `templates/municipios/avaliacao-painel.html`

---

## 2026-06-10 — `ce03282`

### Docs — Datas preenchidas no histórico de design.md

- Tabela do histórico de alterações em `docs/design.md` com as datas corretas de todos os commits

**Arquivos:** `docs/design.md`

---

## 2026-06-10 — `2db2dfd`

### Docs — Documentação completa de design da plataforma

- Criado `docs/design.md` com histórico e decisões de design desde o primeiro commit
- Cobre: identidade visual, tipografia, design system, componentes globais, todas as páginas, responsividade, acessibilidade e melhorias de UX/UI

**Arquivos:** `docs/design.md`

---

## 2026-06-10 — `f8cb3e3`

### Fix — Scroll-to-top oculto em páginas de mapa

- Botão `.rb-scroll-top` ocultado com `display: none !important` nas páginas `body.mapa-page` e `body.np-body` para evitar conflito com a legenda do mapa no canto inferior direito

**Arquivos:** `static/css/components.css`

---

## 2026-06-10 — `5380679`

### Style — Logos parceiros no rodapé reduzidos para 44px

- `.rb-footer-logo { height: 72px → 44px; max-width: 150px → 110px }` para melhor harmonia com o restante do rodapé

**Arquivos:** `static/css/base.css`

---

## 2026-06-10 — `f4682bb`

### Feat — 23 melhorias de UX/UI em toda a plataforma

**Alta prioridade:**

- Tratamento de erros de API com feedback visual em Avaliação Painel e Painel Multinível
- Navegação por teclado ArrowLeft/Right/Home/End nos tab bars
- FAB some ao abrir sidebar no mobile (classe `body.mg-sidebar-open`)
- Remove delay de 350ms no fechamento da sidebar do mapa

**Média prioridade:**

- Empty state com ícone SVG clipboard e texto estruturado na Avaliação Painel
- Badge contador de filtros ativos no botão "Limpar filtros" do mapa
- Normalização de `stroke-width="2"` em todos os loaders SVG
- Botão scroll-to-top global (aparece após 400px de scroll)
- Fade suave (opacity 0.25 → 1) nos gráficos de Financiamento ao trocar filtros
- Opacidade dos ícones de tab inativo: 0.72 → 0.88

**Baixa prioridade:**

- Componentes `.rb-page-intro` e `.rb-empty-state` padronizados em `components.css`
- Persistência de filtros do mapa via localStorage (`mg-filtros`)
- Tooltips nativos (`title=""`) nos valores KPI do Painel Multinível

**Arquivos:** `static/js/avaliacao-painel.js`, `static/js/painel-multinivel.js`, `static/js/mapa-georreferenciado.js`, `static/js/financiamento-climatico.js`, `templates/municipios/avaliacao-painel.html`, `templates/municipios/mapa-georreferenciado.html`, `templates/municipios/painel-multinivel.html`, `base_templates/base.html`, `static/css/avaliacao-painel.css`, `static/css/painel-multinivel.css`, `static/css/mapa-georreferenciado.css`, `static/css/components.css`

---

## 2026-06-10 — `9ac604a`

### Feat — Design system completo: tokens.css + components.css

- Criado `static/css/tokens.css` com todos os design tokens (cores, gradientes, sombras, raios, transições) como CSS custom properties
- Criado `static/css/components.css` com classes reutilizáveis entre páginas usando multi-seletores (elimina CSS duplicado sem alterar HTML)
- `base.html` carrega `tokens.css` → `components.css` → `base.css` → CSS de página
- Removidas definições duplicadas de `.pm-panel-card`, `.ap-card`, `.pm-card-header`, `.ap-card-header`, `.pm-criteria-badge`, `.ap-ficha-btn` dos arquivos de página

**Arquivos:** `static/css/tokens.css` (novo), `static/css/components.css` (novo), `base_templates/base.html`, `static/css/painel-multinivel.css`, `static/css/avaliacao-painel.css`

---

## 2026-06-09 — `d82d7b6`

### Chore — Polimento profissional em toda a plataforma

- Meta tags Open Graph e Twitter Card em todas as páginas
- Favicon SVG + `<link rel="apple-touch-icon">` em `base.html`
- Ano do copyright dinâmico: `{% now "Y" %}` no rodapé
- Typo corrigido: "Inicio" → "Início" nos templates e nav
- `scroll-behavior: smooth` no seletor `html`
- `@media print` styles nos painéis (Painel Multinível e Avaliação)
- `robots.txt` servido via Django TemplateView
- Card "Ecossistema" (em breve): link morto substituído por `<span aria-disabled="true">` + badge "Em breve"
- `loading="lazy"` em imagens não críticas da landing

**Arquivos:** `base_templates/base.html`, `static/css/base.css`, `static/css/painel-multinivel.css`, `static/css/avaliacao-painel.css`, `templates/municipios/landing.html`, `setup/urls.py`

---

## 2026-06-08 — `55ef5ec`

### Feat — Acessibilidade WCAG 2.1 AA em toda a plataforma

- Skip link `<a href="#rb-main-content">` visível no foco em `base.html`
- `role="tablist"`, `role="tab"`, `role="tabpanel"` nos tab bars de Painel Multinível e Avaliação
- `aria-selected`, `aria-controls`, `aria-labelledby` atualizados dinamicamente ao trocar abas
- `aria-live="polite"` na área da tabela de avaliação
- Trap de foco no modal Ficha Técnica (Tab/Shift+Tab + Escape fecha o modal)
- `aria-hidden="true"` em todos os SVGs decorativos
- `alt=""` em ícones de tab (decorativos)
- `role="status"` em loaders e placeholders
- Contraste de todos os textos principais verificado (≥ 4.5:1)

**Arquivos:** `base_templates/base.html`, `templates/municipios/painel-multinivel.html`, `templates/municipios/avaliacao-painel.html`, `templates/municipios/mapa-georreferenciado.html`, `templates/municipios/nota-pais.html`, `static/js/avaliacao-painel.js`, `static/js/painel-multinivel.js`

---

## 2026-05-28 — `f4649e0`

### Style — Remove texturas e aplica cor sólida no header e rodapé

- Header e rodapé: `background: #1B3333` sólido (removida imagem `bg-header.png` e overlay)
- Fundo global: `background: #bdd6e0` sólido (removida imagem `bg-body.png`)
- Onda do footer: `fill: #bdd6e0` alinhado ao novo fundo

**Arquivos:** `static/css/base.css`, `base_templates/base.html`

---

## 2026-05-25 — `dc69471` / `f54ef12`

### Feat — Header reorganizado em 3 colunas, logo Radar Brasil adicionado

- Layout do header reestruturado: `[logo-radar] [título + subtítulo] [logo-FNP]` em 3 colunas
- Nav (`rb-main-nav`) movida para fora do wrapper do header
- Logo Radar Brasil (SVG) adicionado no canto esquerdo com link para a landing page
- Logo FNP harmonizada no canto direito com link externo para fnp.org.br

**Arquivos:** `base_templates/base.html`, `static/css/base.css`

---

## 2026-05-25 — `181ea3a` / `f104f2a` / `42e60f9` / `e1777cf`

### Fix — Mobile: rodapé, header e tabela de Financiamento

- Rodapé mobile: redesign completo em coluna única com logos e tipografia ajustadas
- Header mobile: logo Radar Brasil visível com layout harmônico 3 colunas
- Tabela de Financiamento Climático: layout de card no mobile (cada linha vira card com `data-label`)
- Financiamento Climático mobile: melhoria estética geral (dropdowns, gráficos)

**Arquivos:** `static/css/base.css`, `static/css/financiamento-climatico.css`, `templates/municipios/financiamento-climatico.html`

---

## 2026-05-22 — `46cc5a5`

### Chore — Design tokens iniciais + ferramentas de qualidade e CI

- Aliases semânticos adicionados ao `:root` em `base.css`: `--color-primary`, `--color-primary-dark`, `--color-text-*`, `--color-bg-*`, `--color-border-*`, `--font-*`, `--radius-*`, `--shadow-*`, `--transition-*`
- `.flake8` e `pyproject.toml` (Black + isort) configurados
- GitHub Actions CI configurado

**Arquivos:** `static/css/base.css`, `.flake8`, `pyproject.toml`, `.github/workflows/ci.yml`

---

## 2026-05-19 — `ab11c10`

### Feat — Landing page vira página inicial da aplicação (`/`)

- Rota `/` aponta para a landing page (antes apontava para `/inicio/`)
- Início (`/inicio/`) mantido como página de acesso rápido

**Arquivos:** `setup/urls.py`, `apps/indicadores/urls.py`

---

## 2026-05-18 — `6f1eb79` / `29af3dc` / `92234a3` / `f4a9faa` / `e9f6e87` / `cc127c2`

### Style — Landing page: bolinha verde pulsante e novas miniaturas dos cards

- Badge pill verde pulsante (CSS animation) nas seções Início e Metodologia
- Miniaturas dos cards da landing atualizadas com novas ilustrações SVG
- Fundo das miniaturas padronizado em branco com `object-fit: contain`
- Travessão decorativo removido do card hero

**Arquivos:** `static/css/landing.css`, `templates/municipios/landing.html`, `static/img/`

---

## [Não publicado] — 2026-05-21

### Padronização — Design tokens, qualidade de código e CI

**CSS Design Tokens** (`static/css/base.css`)

- Adicionados aliases semânticos ao `:root` existente: `--color-primary`, `--color-primary-dark`, `--color-primary-deep`, `--color-text-*`, `--color-bg-*`, `--color-border-*`, `--font-sans/display/ui`, `--radius-*`, `--shadow-*`, `--transition-*`, `--ease-*`
- As variáveis `--hdr-*` e `--bdy-*` existentes foram mantidas para compatibilidade retroativa

**Configuração de qualidade** (`.flake8`, `pyproject.toml`)

- `.flake8`: max-line-length 100, exclude migrations/.venv, per-file-ignores para arquivos gerados pelo Django
- `pyproject.toml`: configuração do Black (line-length 100, target Python 3.12) e isort
- Formatação Black aplicada em 17 arquivos Python (sem mudança de comportamento)
- Corrigida variável não usada `ente_col` em `financiamento_climatico.py`
- Corrigida linha longa em `painel_multinivel.py`
- Flake8 passa sem erros; Black passa sem reformatações

**Documentação de ambiente** (`.env.example`)

- Template com todas as variáveis necessárias e comentários em português

**Política de segurança** (`SECURITY.md`)

- Documento de divulgação responsável e tabela de configurações ativas em produção

**Guia de contribuição** (`CONTRIBUTING.md`)

- Fluxo Git completo (feature → next → main), padrão de commit, estrutura de arquivos, padrões de CSS/JS/Python

**GitHub Actions CI** (`.github/workflows/ci.yml`)

- Pipeline CI que roda em push para `next`/`main` e PRs para `next`
- Etapas: `flake8` → `black --check` → `pytest` (com SQLite em memória, sem PostgreSQL)

**Arquivos:** `static/css/base.css`, `.flake8`, `pyproject.toml`, `.env.example`, `SECURITY.md`, `CONTRIBUTING.md`, `.github/workflows/ci.yml`, `apps/indicadores/services/financiamento_climatico.py`, `apps/indicadores/services/painel_multinivel.py`

---

### Dev — Ferramentas de qualidade e suite de testes

- Criado `requirements-dev.txt` com `black`, `flake8`, `pytest-django`, `pytest-cov` — **não enviado ao Render**, apenas para uso local
- Criado `pytest.ini` apontando para `setup.settings`
- 13 testes em `apps/indicadores/tests.py` cobrindo todos os endpoints da API e páginas principais: status HTTP, formato JSON, validação de parâmetros, respostas padrão sem filtros, e blindagem contra injeção em parâmetros de query string
- Todos os 13 testes passam localmente em 13s

**Arquivos:** `requirements-dev.txt`, `pytest.ini`, `apps/indicadores/tests.py`

---

### Fix — Posicionamento dos labels de países no mapa Nota País

- Adicionado `LABEL_OVERRIDES` (~110 entradas) com coordenadas corretas para países problemáticos: territórios ultramarinos (França, Reino Unido, Dinamarca/Groenlândia, Noruega/Svalbard), arquipélagos (Filipinas, Indonésia, Japão), países compridos (Chile, Rússia), ilhas pequenas (Caribe, Oceania, África)
- Adicionada função `ringArea` (fórmula de Shoelace) para calcular área real de anéis poligonais
- Corrigida função `getCentroid`: MultiPolygon agora seleciona o polígono com **maior área** (`ringArea`) em vez de maior número de pontos — evita que países com muitas ilhas pequenas tenham o centróide na ilha errada
- `buildMap` agora usa `LABEL_OVERRIDES[iso] || getCentroid(feature)` tanto para países signatários (pin + label) quanto não-signatários (label)

**Arquivo:** `static/js/nota-pais.js`

---

## [Não publicado] — 2026-05-20

### Mobile UX — Filtros como bottom sheet com FAB flutuante (Mapas)

Padrão inspirado no projeto IFEM aplicado a **Mapa Georreferenciado** e **Nota País**:

- Mapa ocupa 100% da área disponível em mobile (sidebar removida do fluxo)
- Botão FAB circular flutuante (ícone de filtro) no canto inferior esquerdo do mapa
- Toque no FAB → painel desliza de baixo para cima (bottom sheet, `max-height: 78vh`)
- Drag handle visual (pill cinza) no topo do painel indica que é arrastável
- Backdrop semitransparente cobre o mapa; toque fora ou no botão X fecha o painel
- `document.body.style.overflow = 'hidden'` enquanto painel está aberto (previne scroll do body)
- Em ≤480px: intro text oculta para maximizar área do mapa; mapa ocupa 65-70vh

**Arquivos:** `static/css/mapa-georreferenciado.css`, `static/css/nota-pais.css`, `templates/municipios/mapa-georreferenciado.html`, `templates/municipios/nota-pais.html`

---

### Mobile UX — Abas com largura igual (flex:1) preenchendo a barra inteira

- Adicionado `flex: 1` em cada `li` das abas a ≤480px — abas ocupam largura igual e preenchem 100% da barra, eliminando o scroll horizontal (padrão nativo iOS/Android)
- Label abreviado ajustado de 9px para 9.5px para melhor legibilidade
- `overflow-x: visible` no card-header a ≤480px para cancelar o scroll ativado em 900px
- `width: 100%` no button para que o clique funcione em toda a área da aba

**Arquivos:** `static/css/painel-multinivel.css`, `static/css/avaliacao-painel.css`

---

### Mobile UX — Abas com ícone + label abreviado (padrão iOS/Android)

- Substituído layout de ícone-somente a ≤480px por coluna ícone+label nas páginas **Painel Multinível** e **Avaliação Painel Multinível**
- Adicionado atributo `data-short` nos `<span>` das abas com versões abreviadas: "Govern.", "Políticas", "Programas", "Financ."
- CSS usa `font-size: 0` no span + `::after { content: attr(data-short); font-size: 9px }` para exibir o label abreviado sem duplicar markup
- Botão reestruturado com `flex-direction: column; gap: 3px` — segue padrão de tab bar nativo mobile
- Cor do label herda da cor do botão (inativo: teal translúcido; ativo: navy escuro)

**Arquivos:** `static/css/painel-multinivel.css`, `static/css/avaliacao-painel.css`, `templates/municipios/painel-multinivel.html`, `templates/municipios/avaliacao-painel.html`

---

## [Não publicado] — 2026-05-19

### Security Hardening — Auditoria OWASP aplicada

- **SECRET_KEY**: sem valor padrão em produção — levanta `ImproperlyConfigured` se ausente
- **DEBUG**: forçado `False` quando `ENV=production`, independente da variável `DEBUG`
- **ALLOWED_HOSTS**: removido wildcard `*`; fallback para `localhost` apenas em dev; em produção exige configuração explícita
- **Headers HTTP**: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `XSS-Protection`, `Referrer-Policy: strict-origin-when-cross-origin`
- **HTTPS em produção**: HSTS 1 ano + `includeSubDomains` + `preload`, `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER` para proxy do Render
- **Cookies seguros**: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_HTTPONLY` em produção
- **Logging estruturado**: exceções internas logadas com `logger.exception()`; respostas de erro retornam mensagem genérica (sem expor stack trace ao cliente)
- **Validação de input**: parâmetro `?eixo=` validado contra whitelist `_EIXOS_VALIDOS` antes de consultar serviços
- **REST Framework**: `DEFAULT_PERMISSION_CLASSES` definido explicitamente como `AllowAny`

**Arquivos:** `setup/settings.py`, `apps/indicadores/views.py`

---

## [Não publicado] — 2026-05-18

### Nota País — Print exibe apenas países signatários

- `imprimirMapa()` agora oculta temporariamente todos os labels de países não-signatários (`np-country-label--minor`) antes de capturar o canvas via html2canvas
- Após a captura (sucesso ou erro), os labels são restaurados automaticamente no `finally`
- Adicionado campo `signatory: true/false` em cada item do array `labelMarkers` durante `buildMap()` para diferenciar signatários de não-signatários sem varredura de DOM

**Arquivos:** `static/js/nota-pais.js`

---

## [Não publicado] — 2026-05-15

### Mapa Georreferenciado — Filtro cascata Região → Estado

- Adicionado mapeamento fixo `REGIAO_UFS` no JS: Norte, Nordeste, Centro-Oeste, Sudeste, Sul com suas respectivas siglas de UF
- Adicionada variável `allUfOptions` para guardar todas as opções de estado após o primeiro carregamento
- Nova função `atualizarEstadosPorRegiao(regiao)`: reconstrói o select de Estado exibindo apenas os estados da região selecionada; ao limpar a região restaura todos os estados
- Listener do select `#mg-f-regiao` atualizado para chamar `atualizarEstadosPorRegiao` antes de filtrar
- `limparFiltros()` atualizado para restaurar todos os estados via `atualizarEstadosPorRegiao("")`

**Arquivos:** `static/js/mapa-georreferenciado.js`

---

## 2026-05-15 — `0816524`

### Redesign Metodologia + legibilidade Nota País + link Mapa na Landing

- Metodologia: hero reformulado com badge pill, `h1` em `#1a2e3a` com `<em>` em `#356073`, layout grid 2 colunas `1fr 400px`
- Metodologia: cards de passo com glassmorphism (`rgba(255,255,255,.72)`, backdrop-filter), cabeçalho com gradiente escuro
- Metodologia: animações de entrada (hero translateX, seções translateY staggered, count-up nos KPIs)
- Nota País: labels de países não-signatários: opacidade elevada de `.48` → `.80`, tamanho `6px` → `7px`, peso `500` → `600`
- Nota País: labels principais: opacidade `.72` → `.90`, text-shadow reforçado (tripla camada)
- Landing: botão "Explorar mapa" do Card 03 agora aponta para `{% url 'indicadores:mapa_georreferenciado' %}`

**Arquivos:** `static/css/metodologia.css`, `templates/municipios/metodologia.html`, `static/css/nota-pais.css`, `templates/municipios/landing.html`

---

## 2026-05-14 — `e0565ff`

### Redesign visual global — background azul claro, header/rodapé verde escuro, menu branco

- `body.rb-body` agora usa `background: #bdd6e0` em vez de `bg-body.png` em todos os arquivos
- Painel Multinível (`inicio.css`, `painel-multinivel.css`), Avaliação Painel (`avaliacao-painel.css`) e Linha do Tempo (`linha-do-tempo.css`) atualizados com o novo background
- Menu de navegação: `background: #ffffff` (era glassmorphism com backdrop-filter)
- Header e footer: `background-color: #061e1b` com overlay escuro sobre `bg-header.png`
- Logo: `filter: brightness(0) invert(1); opacity: 0.85` para adaptar ao header escuro
- Onda do footer: `fill: #bdd6e0` para combinar com o fundo da página
- Landing page: `body.lp-body { background: #bdd6e0 }` e onda do footer atualizada

**Arquivos:** `static/css/base.css`, `base_templates/base.html`, `static/css/landing.css`, `static/css/inicio.css`, `static/css/painel-multinivel.css`, `static/css/avaliacao-painel.css`, `static/css/linha-do-tempo.css`

---

## 2026-05-14 — `b55d2a2`

### Redesign visual global — glassmorphism e ajustes de UX

- Ícones das imagens `-land.png` adicionados nos cards da landing (computadores, painel, mapa, ecossistema, agenda)
- Cards da landing: container de imagem com `120×90px`, `border-radius: 12px`, fundo glass (`rgba(255,255,255,.80)`), `object-fit: contain`
- Fundo global alterado para `#bdd6e0` (azul claro) em substituição ao `bg-body.png`

**Arquivos:** `templates/municipios/landing.html`, `static/css/landing.css`

---

## 2026-05-13 — `df07405`

### Filtros do popup no Mapa + ícone câmera nos botões + labels no Painel Multinível

- Popup do mapa: filtros de eixo, modalidade e estágio adicionados diretamente no popup de cada município
- Botões de ação: ícone de câmera (`📷`) adicionado no botão Print Mapa
- Painel Multinível: labels e ajustes visuais nos gráficos

**Arquivos:** `static/js/mapa-georreferenciado.js`, `templates/municipios/mapa-georreferenciado.html`

---

## 2026-05-13 — `c37f7f3`

### Filtro de região no Mapa + refatoração gráficos de Financiamento + melhorias visuais

- Mapa Georreferenciado: filtro de Região adicionado ao sidebar (select `#mg-f-regiao`)
- Mapa: filtragem por região via campo `regiao` no GeoJSON
- Financiamento Climático: refatoração dos três gráficos (setor, origem, ente) com melhoria de legibilidade
- Melhorias visuais gerais de alinhamento e espaçamento

**Arquivos:** `static/js/mapa-georreferenciado.js`, `templates/municipios/mapa-georreferenciado.html`, `static/js/financiamento-climatico.js`

---

## 2026-05-12 — `288fa4f`

### Legenda interativa no gráfico Origem dos Recursos

- Gráfico de Origem dos Recursos: legenda clicável que mostra/oculta barras individualmente
- Scroll automático quando há muitos itens (`max-height: 280px` no container)

**Arquivos:** `static/js/financiamento-climatico.js`

---

## 2026-05-12 — `d4dd9bd`

### Página Nota País + ajustes Financiamento Climático + padronização do header

- Implementação completa da página Nota País com mapa-múndi Leaflet
- Países CHAMP Signatários coloridos por continente com pinos vermelhos e labels
- Filtro de região funcional (Américas, Europa, África, Ásia, Oceania)
- KPI strip com 4 métricas estáticas
- Tooltip especial amarelo para o Brasil (Nível 3,0)
- Labels dos oceanos em itálico azul semi-transparente
- Labels de países não-signatários em texto menor

**Arquivos:** `templates/municipios/nota-pais.html`, `static/css/nota-pais.css`, `static/js/nota-pais.js`, `apps/indicadores/views.py`, `apps/indicadores/urls.py`

---

## 2026-05-12 — `788d560`

### Página Financiamento Climático com gráficos, filtros e tabela paginada

- Implementação completa: MultiSelect dropdowns, três gráficos Plotly (setor, origem, ente federado)
- Tabela paginada (10 por página) com exportação CSV + BOM UTF-8
- Serviço Python de leitura do Google Sheets com cache de 30 min

**Arquivos:** `templates/municipios/financiamento-climatico.html`, `static/css/financiamento-climatico.css`, `static/js/financiamento-climatico.js`, `apps/indicadores/services/financiamento_climatico.py`

---

## 2026-05-11 — `bf8f74d`

### Botão limpar município + legenda adaptável + tiles OSM pt-br

- Campo de busca de município: botão `×` de limpar exibido condicionalmente
- Legenda do mapa adaptada ao estado do toggle "sem financiamento"
- Tiles do mapa: provider OpenStreetMap em português do Brasil

**Arquivos:** `static/js/mapa-georreferenciado.js`, `templates/municipios/mapa-georreferenciado.html`

---

## 2026-05-11 — `4f661d9`

### Mapa em português + toggle sem financiamento + ajustes visuais

- Toggle "Exibir sem financiamento" implementado (exibe municípios sem financiamento em laranja-vermelho)
- Mapa com tiles em português do Brasil

**Arquivos:** `static/js/mapa-georreferenciado.js`

---

## 2026-05-11 — `cfae653`

### Redesign do popup do Mapa Georreferenciado

- Popup reformulado com informações completas do município: nome, UF, região, porte, eixos e valores
- Layout visual aprimorado com tipografia clara e separação de seções

**Arquivos:** `static/js/mapa-georreferenciado.js`, `static/css/mapa-georreferenciado.css`

---

## 2026-05-08 — `557d16d`

### Redesign cards da página Início + estilos da Metodologia

- Cards da página Início redesenhados com visual glassmorphism alinhado à Metodologia

**Arquivos:** `static/css/inicio.css`, `templates/municipios/inicio.html`

---

## 2026-05-08 — `b564640`

### Filtros Financiamento e Porte Populacional + painel de totais no Mapa

- Select de Financiamento (eixo) e Porte Populacional adicionados ao sidebar do mapa
- Painel de totais exibido sobre o mapa: valor total estimado e contagem de municípios filtrados

**Arquivos:** `static/js/mapa-georreferenciado.js`, `templates/municipios/mapa-georreferenciado.html`, `static/css/mapa-georreferenciado.css`

---

## 2026-05-07 — `03c178f`

### Implementação da página Mapa Georreferenciado

- Página completa com Leaflet.js, marcadores circulares por município, sidebar de filtros
- Filtros: eixo, modalidade, estágio, executor, UF, município (texto livre)
- Overlay GeoJSON simplificado do Brasil
- Popup com detalhes do município ao clicar no marcador
- Botões: Limpar filtros, Baixar CSV, Print Mapa (html2canvas)

**Arquivos:** `templates/municipios/mapa-georreferenciado.html`, `static/css/mapa-georreferenciado.css`, `static/js/mapa-georreferenciado.js`, `apps/indicadores/views.py`, `apps/indicadores/urls.py`, `apps/indicadores/services/mapa_georreferenciado.py`

---

## 2026-05-07 — `51b9b82`

### Página Linha do Tempo + botões PDF e Linha do Tempo na Ficha Técnica

- Implementação da página Linha do Tempo com eventos cronológicos
- Ficha Técnica do modal de avaliação: botões PDF e navegação para Linha do Tempo adicionados

**Arquivos:** `templates/municipios/linha-do-tempo.html`, `static/css/linha-do-tempo.css`, `static/js/avaliacao-painel.js`

---

## 2026-05-06 — `bec297a`

### Contraste dos rótulos na Ficha Técnica do modal de avaliação

- Rótulos da ficha técnica: contraste elevado para maior legibilidade

**Arquivos:** `static/css/avaliacao-painel.css`

---

## 2026-05-06 — `4d9a97e`

### Botão Critérios e Parâmetros redireciona para aba correta

- Clique no botão "Critérios e Parâmetros" abre o Painel Multinível na aba correta via query param `?eixo=`

**Arquivos:** `static/js/avaliacao-painel.js`

---

## 2026-05-05 — `b283ffa`

### Implementação da página Avaliação Painel Multinível

- Página completa com 4 abas de eixo (Governança, Políticas e Planos, Programas, Linhas de Financiamento)
- Filtros em cascata: Setor → Estrutura
- Tabela de avaliação com colunas de critério, pontuação e nível
- Modal de Ficha Técnica com detalhes completos de cada estrutura avaliada
- Botões de PDF, Linha do Tempo e navegação para Painel Multinível

**Arquivos:** `templates/municipios/avaliacao-painel.html`, `static/css/avaliacao-painel.css`, `static/js/avaliacao-painel.js`, `apps/indicadores/views.py`, `apps/indicadores/urls.py`

---

## 2026-05-05 — `52bb8b1` / `0b1f5e9`

### Alinhamento visual de Painel Multinível e Início à Metodologia

- Painel Multinível e página Início alinhados ao padrão visual da Metodologia (glassmorphism, cores)

**Arquivos:** `static/css/painel-multinivel.css`, `static/css/inicio.css`

---

## 2026-05-05 — `ac394c4`

### Fix: seleção de aba no Painel Multinível por query param

- Corrigida a lógica de ativação de aba quando a URL contém `?eixo=`

**Arquivos:** `static/js/painel-multinivel.js`

---

## 2026-05-04 — `091f596`

### Redesign da página Metodologia com glassmorphism e hero zone

- Metodologia: hero zone com imagem de fundo, badge, título em destaque
- Cards de passo com estilo glassmorphism
- Estágio visual alinhado ao resto do projeto

**Arquivos:** `static/css/metodologia.css`, `templates/municipios/metodologia.html`

---

## 2026-04-30 — `9874dbb`

### Fix: espaçamento acima do header

- Corrigido espaço excessivo entre o topo da janela e o header em todas as páginas

**Arquivos:** `static/css/base.css`

---

## 2026-04-24 — `41c5600`

### Implementação do Painel Multinível com dados do Google Sheets e Chart.js

- Painel Multinível: 4 abas de eixo, gráfico de barras horizontais empilhadas (Chart.js)
- Plugin `barLabels` customizado para exibir valores dentro das barras
- Integração com API Django que lê dados do Google Sheets
- Filtros de UF e Município

**Arquivos:** `templates/municipios/painel-multinivel.html`, `static/css/painel-multinivel.css`, `static/js/painel-multinivel.js`, `apps/indicadores/services/painel_multinivel.py`

---

## 2026-04-24 — `9a7fa06`

### Padronização do header e barra de menu em todas as páginas

- Header e barra de navegação padronizados: altura, cores, logo e links consistentes em todas as páginas

**Arquivos:** `static/css/base.css`, `base_templates/base.html`

---

## 2026-04-22 — `5eecb76`

### Estrutura base: Painel Multinível, Metodologia, Landing e Google Sheets

- Estrutura inicial das páginas Painel Multinível, Metodologia e Landing
- Configuração da integração com Google Sheets (Service Account, `gspread`)

**Arquivos:** `apps/indicadores/services/`, `base_templates/base.html`, `templates/municipios/`

---

## 2026-04-22 — `c70ad94`

### Implementação da página de Metodologia com cards e ícones SVG

- Metodologia: cards explicativos com ícones SVG, layout responsivo

**Arquivos:** `templates/municipios/metodologia.html`, `static/css/metodologia.css`

---

## 2026-04-15 — `0184cea`

### Implementação do layout da página Início

- Página Início implementada com os cards de navegação para cada seção do Radar Brasil

**Arquivos:** `templates/municipios/inicio.html`, `static/css/inicio.css`

---

## 2026-04-14 — `9f16467`

### Primeiro commit do projeto Radar Brasil

- Estrutura inicial do projeto Django
- Configuração do ambiente, apps, URLs e templates base

**Arquivos:** todos os arquivos de estrutura do projeto
