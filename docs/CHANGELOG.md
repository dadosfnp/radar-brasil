# CHANGELOG — Radar Brasil

Histórico cronológico de todas as alterações realizadas no projeto.

---

## [Não publicado] — 2026-05-20

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
