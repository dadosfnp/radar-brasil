# CLAUDE.md — Contexto do Projeto Radar Brasil

> Arquivo de contexto para sessões com Claude Code. Atualizado ao final de cada expediente.
> Última atualização: 2026-09-04

---

## Visão Geral

**Radar Brasil** é uma plataforma Django para monitoramento do federalismo climático brasileiro. Permite avaliar, comparar e explorar dados climáticos de municípios em todo o território nacional. Desenvolvida pela FNP — Frente Nacional de Prefeitas e Prefeitos.

URL de produção: `https://radarbrasil.fnp.org.br` (DigitalOcean droplet `fnp-web`, branch `main`)
Branch de desenvolvimento ativo: `next`

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 6.0.4 · Python 3.12 |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL 18 — DigitalOcean Managed (`fnp-database`) |
| Sincronização de dados | gspread (Google Sheets) · pandas — apenas no `sync_sheets_db` |
| Deploy | Docker + Gunicorn + Nginx — droplet `fnp-web` |
| Mapas | Leaflet.js · html2canvas |
| Estáticos | WhiteNoise |
| Env vars | python-dotenv |
| i18n | Django LocaleMiddleware + i18n.js (RBi18n) |

---

## Estrutura de Arquivos

```
apps/
  indicadores/
    views.py           ← views Django (render + JsonResponse)
    urls.py            ← rotas das páginas e APIs
    models.py          ← RegistroFicha, RegistroParametro, RegistroFinanciamento, RegistroMapa
    services/
      avaliacao_painel.py        ← Painel Multinível (fichas técnicas) — lê do ORM
      painel_multinivel.py       ← scores/critérios por eixo — lê do ORM
      financiamento_climatico.py ← tabela de financiamentos — lê do ORM
      mapa_georreferenciado.py   ← dados do mapa Leaflet — lê do ORM
      sheets_reader.py           ← lê Google Sheets — usado APENAS pelo sync_sheets_db
    management/commands/
      sync_sheets_db.py          ← importa Sheets → PostgreSQL (rodar ao atualizar planilhas)
  municipios/          ← views e urls principais
  usuarios/            ← autenticação
static/
  css/                 ← um arquivo por página
  js/                  ← um arquivo por página
  img/
templates/municipios/  ← templates por página
base_templates/        ← base.html (header, footer, lang selector)
locale/
  en/LC_MESSAGES/
    django.po          ← traduções EN (243 strings)
    django.mo          ← compilado (gerado por compilemessages)
setup/                 ← settings.py, urls.py, wsgi.py
deploy/
  nginx-radarbrasil.conf ← configuração Nginx (copiada para /etc/nginx/sites-available/ no droplet)
docs/
  CHANGELOG.md         ← histórico completo de alterações
  design.md            ← decisões e alterações de design
Dockerfile             ← Python 3.12-slim, appuser UID 1000, porta 8005
entrypoint.sh          ← migrate + collectstatic + gunicorn (roda no container)
docker-compose.yml     ← serviço radarbrasil, porta 127.0.0.1:8005
.env.example           ← template das variáveis de ambiente
```

---

## Git — Remotos

O projeto tem **dois remotos**:

| Remoto | URL | Uso |
|---|---|---|
| `origin` | `https://github.com/brunofnp/radar-brasil.git` | Repositório pessoal — CI GitHub Actions |
| `prod` | `https://github.com/dadosfnp/radar-brasil.git` | Repositório da organização FNP |

**CRÍTICO:** Para subir para produção é obrigatório fazer push nos dois:
```powershell
git push origin main
git push prod main
```
Depois, no droplet (`ssh root@142.93.205.222`):
```bash
cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
```

---

## Fontes de Dados — Google Sheets → PostgreSQL

O runtime **não acessa** o Google Sheets. Os dados ficam no PostgreSQL e são atualizados via:

```bash
docker compose exec radarbrasil python manage.py sync_sheets_db
```

O comando lê as planilhas abaixo, normaliza os dados e faz `bulk_create` no banco (apaga e reinsere por idioma).

### Planilhas PT

| Tabela | Sheet ID | GID / worksheet |
|---|---|---|
| Fichas | `16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8` | worksheet "dados" |
| Parâmetros | `1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE` | worksheet "dados" |
| Financiamento | `1sxKa2yu8GL8U6m4zoK42hO75a-YZqVKK5PKNJ8jlJ8c` | GID `793540087` |
| Mapa | `1qMPAIB5e6IoG_cdCpBMIgzG8fZS1wUZ1zQbOFW3jACs` | GID `1619423236` |

### Planilhas EN

| Tabela | Sheet ID | GID |
|---|---|---|
| Fichas EN | `1EkaWJ2n391vXukwsNTGj-RMd65S55hADtR24lxRXx9g` | `1400373985` |
| Parâmetros EN | `1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8` | `1708988989` |
| Financiamento EN | `1bQoDf4AEElaNy6_vUQSh-tOoZDKZA-R7mEn2eUmZEmk` | `449650871` |
| Mapa EN | `1uj_8PdAvTScqxSGi0ujBCRhiuJgXXFeaZFO8B4qJtqk` | primeira aba |

**Credenciais:** `GOOGLE_SHEETS_CREDS_JSON` no `.env` do droplet (JSON da service account em linha única). Arquivo local: `.secrets/fnp-radar-sheets.json`.

**Colunas relevantes (fichas):**
- `Link_eixo` — URL do eixo (usado no título da ficha técnica)
- `Link_orgao` — URL do órgão responsável
- `Link_arcabouco` — URL do arcabouço normativo

**Critérios renomeados (`painel_multinivel.py`):**
- `Sustentabilidade Financeira` (era "Financiamento")
- `Diversidade e Representatividade` (era "Representação de Gênero, Raça e Etnia")

---

## Sistema i18n

### Django (templates)

- `LocaleMiddleware` em `MIDDLEWARE` no `settings.py`
- `LANGUAGES = [("pt-br", "Português"), ("en", "English")]`
- Seletor PT|EN no header (via `set_language` em `/i18n/setlang/`)
- Templates usam `{% load i18n %}` + `{% trans "..." %}`
- `request.LANGUAGE_CODE` renderizado como `lang="{{ request.LANGUAGE_CODE }}"` no `<html>`
- Arquivo PO: `locale/en/LC_MESSAGES/django.po` (245+ strings)
- Compilar no droplet: `python manage.py compilemessages`
- Compilar localmente (sem msgfmt): `pip install polib` e depois:
  ```python
  import polib; po = polib.pofile("locale/en/LC_MESSAGES/django.po"); po.save_as_mofile("locale/en/LC_MESSAGES/django.mo")
  ```
  O script `compile_po.py` referenciado anteriormente **não existe** no repositório.

### JavaScript (strings dinâmicas)

Arquivo: `static/js/i18n.js`

```javascript
RBi18n.t("string em português")  // → tradução ou original
RBi18n.getLang()                  // → "pt" ou "en"
```

- Lê `document.documentElement.lang` (definido pelo Django)
- Dicionário `DICT.en` com todas as traduções EN de strings do JS
- Se a string não está no dict, retorna o original (sem erro)

**Problema conhecido — encoding NFC/NFD:**
Strings com ã, ç etc. podem falhar no lookup do dict por discrepância de normalização Unicode entre arquivos. Solução: usar chaves ASCII no dict ou criar dicts paralelos com chaves ASCII (ex.: `EIXO_LABELS_EN` em `avaliacao-painel.js`).

### Normalização EN → PT no sync_sheets_db

As planilhas EN têm cabeçalhos e valores em inglês. O `sync_sheets_db` normaliza antes de salvar:
1. `df.rename(columns=_EN_COLS)` — mapeia nomes de colunas EN → PT
2. `df["Eixo"].replace(_EN_EIXO)` — mapeia valores do eixo EN → PT
3. Regex `Level N → Nível N` na coluna Nível
4. `_EN_CRITERIO` em `painel_multinivel.py` — mapeia critérios EN → PT para lookup em `ORDEM_CRITERIOS`

Os services de runtime (`avaliacao_painel.py`, etc.) leem diretamente do ORM — sem normalização em runtime.

**Quebras de linha em campos de texto (fichas técnicas):**
- `sync_sheets_db`: normaliza `\r\n` e `\r` → `\n` em todos os campos de texto antes de salvar
- Frontend (`avaliacao-painel.js`): converte `\n` → `<br>` ao montar o HTML

---

## CSS — Convenções de Nomenclatura

Cada página tem seu próprio prefixo de classe:

| Prefixo | Página |
|---|---|
| `.ap-` | Avaliação Painel (Multinível) |
| `.mg-` | Mapa Georreferenciado |
| `.fc-` | Financiamento Climático |
| `.np-` | Nota País |
| `.pm-` | Painel Multinível (legado) |

Variáveis globais definidas em `base.css` (`--color-primary`, `--radius-lg`, `--shadow-md`, etc.).  
Design: Glassmorphism com `backdrop-filter`, cards translúcidos, fundo `#bdd6e0`, tipografia Sora + DM Sans + DM Mono.

---

## JS — Arquitetura

- JS vanilla, sem build, sem bundler — um arquivo por página em `static/js/`
- Constantes e dados no topo do arquivo
- `i18n.js` carregado globalmente em `base.html`
- Segurança de hyperlinks: backend valida `url.startswith("http")` antes de retornar; frontend só renderiza `<a>` quando `c.url` é truthy

---

## CI — GitHub Actions

Arquivo: `.github/workflows/ci.yml`

Roda em push para `next` e `main` (remoto `origin`):
1. `flake8 apps setup` — lint Python (max-line-length=100, config em `.flake8`)
2. `black apps setup --check` — formatação Python
3. `pytest apps/indicadores/tests.py -v --tb=short` — 13 testes

**Antes de commitar código Python**: sempre rodar `python -m flake8 apps setup` e `python -m black apps setup --check` localmente.

---

## Git — Fluxo de Trabalho

```
feature/nome  →  next  →  main
bugfix/nome   ↗           ↓
                    push origin main + push prod main
                           ↓
                  DigitalOcean fnp-web (produção)
                  SSH: root@142.93.205.222
                  App: /opt/radar-brasil/
                  docker compose up -d
```

**Regras:**
- Nunca commitar diretamente em `next` ou `main`
- Sempre partir de `next` para criar branches de trabalho
- `main` só recebe via merge de `next`
- Ao subir para produção: `git push origin main` **E** `git push prod main`
- No droplet: `cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d`

---

## Commits — Convenções

Padrão: **Conventional Commits**, descrições em **português**

```
<tipo>: <descrição curta em português>
```

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `style` | Ajuste visual (CSS/HTML sem lógica) |
| `refactor` | Refatoração sem mudança de comportamento |
| `docs` | Documentação |
| `test` | Testes |
| `chore` | Config, dependências, build |
| `perf` | Performance |
| `merge` | Merge de branches |

---

## Regras Obrigatórias de Colaboração com Claude

1. **Nunca** adicionar `Co-Authored-By: Claude` em commits — autor sempre é `brunofnp`
2. **Nunca** inserir "Generated with Claude Code" no corpo de PRs
3. **Todo commit** deve incluir atualização de `docs/CHANGELOG.md` no mesmo commit
4. **Toda alteração de design** deve ser registrada em `docs/design.md` antes do commit
5. Commits via PowerShell: usar variável `$msg = @'...'@` + `git commit -m $msg` para evitar problemas com acentos
6. **Produção** exige push nos dois remotos: `git push origin main` + `git push prod main`

---

## Estado Atual do Projeto (2026-09-04)

### Branch atual: `main` — `983067b` — droplet pendente de rebuild

### Remotos

| Remoto | `next` | `main` |
|---|---|---|
| `origin` (brunofnp) | `983067b` | `983067b` |
| `prod` (dadosfnp) | - | `983067b` |

> `origin` e `prod` identicos em `main`. Branch `next` sincronizado em `origin`.
> Criar feature branches a partir de `next`.

### Git — autenticacao configurada

Remotos `origin` e `prod` configurados com PAT do brunofnp no `.git/config` para push automatico sem prompt interativo. Config apenas local, nao versionada.

### Droplet — pendente de rebuild

Commits `66ef1fc`, `ff45519`, `c1a179e` publicados nos remotos mas **o droplet ainda nao fez build**. Para aplicar:

```bash
cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
```

**CRITICO:** `docker compose up -d` sem `build` nao atualiza arquivos estaticos (WhiteNoise serve de dentro da imagem). Sempre rodar `build` apos mudancas em CSS/JS/templates.

### Infraestrutura de producao

| Item | Valor |
|---|---|
| Droplet | `fnp-web` — Ubuntu 24.04 — `root@142.93.205.222` |
| App dir | `/opt/radar-brasil/` |
| Porta interna | `127.0.0.1:8005` |
| Dominio | `https://radarbrasil.fnp.org.br` |
| SSL | Let's Encrypt via certbot (expira 2026-11-15) |
| Banco | `fnp-database` (DigitalOcean Managed PostgreSQL 18) — database `radar_brasil`, user `radarbrasil` |
| Container | `radarbrasil` — Python 3.12-slim, Gunicorn 3 workers |

### Rotina de deploy

```powershell
# Local
git push origin main
git push prod main
git branch -f next main
git push origin next --force-with-lease

# Droplet (SSH root@142.93.205.222)
cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
```

Para atualizar dados das planilhas (sem redeploy):
```bash
docker compose exec radarbrasil python manage.py sync_sheets_db
```

### Header Global — estado (2026-09-04)

CSS: `static/css/base.css` **v=8** | Template: `base_templates/base.html`

Layout grid 3 colunas `auto 1fr auto` em linha unica, sticky no topo:
- Coluna esquerda: logo Radar Brasil SVG, `height: 124px` desktop / `68px` mobile, `filter: brightness(0) invert(1)`
- Coluna central: `<nav class="rb-main-nav">` — links brancos `rgba(255,255,255,0.78)`, fonte `1.051rem`, active com `border-bottom: 2px solid #fff`
- Coluna direita: logo FNP `height: 62px` desktop / `34px` mobile + pill PT|EN

**Pill PT|EN no mobile (v7/v8):**
- Desktop: `position: absolute; bottom: -26px; right: 16px` (abaixo do logo FNP)
- Mobile (<=768px): `flex-direction: column; align-items: flex-end; gap: 4px` no `.rb-header-logo` + `.rb-lang-form { position: static }` — pill empilha abaixo do logo FNP sem sobreposicao
- Altura total coluna direita no mobile: ~60px (logo 34px + gap 4px + pill ~22px), menor que logo Radar (68px)

**Nav mobile (hamburger):**
- `.rb-nav-links` em mobile: `position: absolute; top: 100%; left: 0; right: 0` — dropdown full-width abaixo do header
- JS (`base.html`): `setNavOpen(open)` — eleva `.rb-header-wrapper` para `z-index: 2300` ao abrir (acima de sidebars z-index: 2100); reseta ao fechar
- Fecha ao clicar fora: `document.addEventListener('click', function(e) { if (!hdr.contains(e.target)) setNavOpen(false); })`
- Barras do hamburger: `background: rgba(255,255,255,0.85)` (era `var(--hdr-700)` = `#101d4f` = invisivel)

**Rodape mobile:**
- `.rb-footer-landing { display: none }` em `<=768px` — removido de todas as paginas no mobile

**Altura do header mobile:** ~88px (wrapper 6+6px + header-top 4+4px + logo 68px)

Nav visivel em TODAS as paginas inclusive landing.

### Pagina Inicio — estado (2026-09-01)

CSS: `static/css/inicio.css` v=12 | Template: `templates/municipios/inicio.html`

Hero layout 46%/54%, `min-height: 320px`, `padding: 32px 0 0`:
- Badge "Federalismo Climatico" — pill com bolinha verde `#22c55e`, `border-radius: 999px`, `padding: 6px 16px`, `background: rgba(38,69,132,.10)`, `border: 1.5px solid rgba(38,69,132,.20)`
- Titulo: `font-size: 2.5rem`, `font-weight: 800`, `color: #101d4f`, `line-height: 1.18`, `font-family: Sora` — dois `{% trans %}` separados: `"Explore os eixos"` + `<br>` + `"do Radar Brasil"`
- Mapa HUD: iframe com `.ini-hud-frame`, `mask-image` degrade; src `mapa-brasil-hud.html?v=3`
- Cards: grid 2x2 glassmorphism. Cards PNG removidos; icone SVG flat sem `radial-gradient`
- Card 4 "Linhas de Financiamento" → `{% url 'indicadores:painel_multinivel' %}?aba=3`

### Mapa Brasil HUD — estado (2026-09-01)

Arquivo: `static/img/mapa-brasil-hud.html` (commitado, nao e um arquivo de imagem estatico)

Elemento `.scene` tem `transform: scale(0.70); transform-origin: 50% 50%` para escalar o mapa interno.
Escalar o `<iframe>` no CSS externo nao afeta o viewport interno — o scale deve estar dentro do HUD.
Iframes nas paginas usam `mask-image` para dissolver bordas.

### Landing Page — estado (2026-09-01)

CSS: `static/css/landing.css` v=11 | Template: `templates/municipios/landing.html`

Hero com iframe HUD animado, grid 44/56%, sidebar "Sobre/Midia/Agenda". Botao "VER AGENDA" desabilitado com `.lp-btn-side--soon` (fundo cinza, cursor default, badge "Em breve").

### Metodologia — estado (2026-09-04)

CSS: `static/css/metodologia.css` **v=22** | Template: `templates/municipios/metodologia.html`

Hero padronizado com Inicio (mesma altura, badge, tipografia).

**Carousel (v22):**
- Label "Federalismo Climático" acima do quote (verde `#22c55e`, uppercase 0.6875rem)
- Quote agora em itálico com aspas HTML ao redor do texto
- Texto-wrap: `flex-direction: column; gap: 14px`

**Timeline redesenhada (v22):**
- Cards alinhados pelo TOPO; linha horizontal movida para a BASE da timeline
- Bolha do ano: pill oval amarela (`#f5c400`), texto navy, substituindo retângulo navy
- Conectores verticais flexíveis entre card e dot; `align-items: stretch` no track
- CSS `order` posiciona card(1) → conector(2) → dot(3) sem alterar HTML

**Seção de Cálculo (v22, nova):**
- Três cards ao final da página: Nível Parcial, Nível Eixo, Nível País
- Fórmulas matemáticas em fração CSS + tabelas de referência
- Nível País: fundo gradient navy; grid 3col desktop / 1col mobile

**Timeline mobile (v22):**
- Em `<=600px`: scroll-x desativado, layout vertical empilhado
- `.meto-tl-year-bubble { order: 1 }` — bolha à esquerda no layout horizontal
- `.meto-tl-connector { display: none }` — conector oculto em mobile
- `.meto-tl-card { order: 3 }` — card à direita da bolha
- Em `<=900px`: `justify-content: flex-start` para evitar corte no scroll-x

### Nota Pais — estado (2026-09-04)

CSS: `static/css/nota-pais.css` **v=9** | Template: `templates/municipios/nota-pais.html`

**Mapa mobile full-screen (Google Maps / IFEM pattern):**
- Em `<=900px`:
  - `.np-intro { display: none }` — removida em mobile (antes so em 480px)
  - `.np-page { padding: 0; gap: 0 }` — sem espaco consumindo viewport
  - `.np-card { height: calc(100svh - 88px); flex-shrink: 0; border-radius: 0; box-shadow: none }` — card define o tamanho
  - `.np-map-container { height: 100% }` — preenche o card pai
- KPI strip scrollavel abaixo do mapa
- Sidebar como bottom sheet (FAB no canto inferior esquerdo do mapa)
- Em `<=480px`: `height: calc(100svh - 96px)` (mantido do breakpoint anterior)

Estrutura HTML:
```
np-page > np-intro + np-card (np-sidebar + np-map-container + np-filter-fab) + np-sidebar-backdrop + np-kpi-strip
```

### Mapa Georreferenciado — estado (2026-09-04)

CSS: `static/css/mapa-georreferenciado.css` **v=7** | Template: `templates/municipios/mapa-georreferenciado.html`

**Mapa mobile full-screen (mesmo padrao que Nota Pais):**
- Em `<=900px`:
  - `.mg-intro { display: none }` — removida em mobile
  - `.mg-page { padding: 0; gap: 0 }`
  - `.mg-layout { height: calc(100svh - 88px); min-height: 0; margin-bottom: 0; border-radius: 0; box-shadow: none }` — layout define o tamanho
  - `.mg-map-area { height: 100%; border-radius: 0 }` — preenche o layout pai
- Em `<=480px`: `height: calc(100svh - 96px)` com `border-radius: 0`

### Painel Multinivel — estado (2026-08-25)

CSS: `static/css/painel-multinivel.css` v=12 | Template: `templates/municipios/painel-multinivel.html`

Grafico fixo em 380px. `_mostrarErroGrafico` esconde `#pm-chart-wrapper` no estado de erro.

### Avaliacao Painel — estado (2026-09-03)

CSS: `static/css/avaliacao-painel.css` v=9 | Template: `templates/municipios/avaliacao-painel.html`

Todos os touch targets elevados para min-height: 44px em mobile.

### Financiamento Climatico — estado (2026-09-03)

CSS: `static/css/financiamento-climatico.css` v=5 | Template: `templates/municipios/financiamento-climatico.html`

Componente MultiSelect com semantica `selected = new Set()` (vazio = todos ativos). Fix iOS mobile aplicado.
Tabela mobile: card layout com `td:first-child` como cabecalho navy.

### Identidade Visual

- `--color-primary`: `#264584` (navy FNP)
- `--color-bg-page`: `#d9e8f5` (azul claro, fundo global)
- Background global: `fundo-bg.png` no elemento `html` (via `base.css`)
- Body das paginas internas: `background: transparent`; body de paginas com hero branco: `background: #ffffff`
- Sem degrades, sem teal/verde (exceto bolinha piscante `#22c55e`)

### i18n EN — completo

- `LocaleMiddleware`, seletor PT|EN no header, `LANGUAGES = [("pt-br",...), ("en",...)]`
- `locale/en/LC_MESSAGES/django.po` — 245+ strings + `django.mo` compilado
- `static/js/i18n.js` — `RBi18n.t()` / `RBi18n.getLang()` — cobre 9 templates + 5 JS
- Banco EN populado (98 fichas, 412 parametros, 46 financiamentos, 2322 mapas)

### Arquitetura de dados

```
Google Sheets → sync_sheets_db → PostgreSQL → Django ORM (runtime)
```

Runtime **nunca** acessa Google Sheets. Para atualizar banco apos editar planilhas:
```bash
docker compose exec radarbrasil python manage.py sync_sheets_db
```

### Arquivos locais nao commitados

| Arquivo | Situacao |
|---|---|
| `static/img/lading-background.jpg` | Untracked (typo no nome: "lading" em vez de "landing") |
| `static/img/radar_brasil_brasilia_alta_qualidade.png` | Untracked |
| `static/img/radar_brasil_mapa_azul_alta_qualidade.png` | Untracked |

Esses arquivos nao foram incorporados a nenhuma pagina e podem ser descartados ou renomeados.

### Versoes atuais dos CSS (cache-busters nos templates)

| Arquivo CSS | Versao no template |
|---|---|
| `base.css` | v=11 |
| `inicio.css` | v=12 |
| `landing.css` | v=11 |
| `metodologia.css` | v=22 |
| `avaliacao-painel.css` | v=11 |
| `painel-multinivel.css` | v=13 |
| `mapa-georreferenciado.css` | v=7 |
| `financiamento-climatico.css` | v=5 |
| `nota-pais.css` | v=9 |

### Pendencias

- **CRITICO:** Droplet nao fez build do commit `983067b` (11 correcoes). Rodar:
  ```bash
  cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
  ```
- Branch `next` sincronizado em `origin` com `983067b`
- DNS do `fnp.org.br` gerenciado em conta DigitalOcean separada ("Nucleo de Dados")

---

## Rotina de Final de Expediente

Quando o usuário sinalizar fim do dia:

1. Atualizar este arquivo (`CLAUDE.md`) com o estado atual do projeto
2. Verificar se `docs/CHANGELOG.md` e `docs/design.md` estão atualizados
3. Confirmar quais commits estão locais e quais foram publicados (origin + prod)
4. Registrar pendências e próximos passos na seção "Estado Atual"

---

## Documentação Técnica

| Arquivo | Conteúdo |
|---|---|
| `docs/CHANGELOG.md` | Histórico completo de todas as alterações |
| `docs/design.md` | Decisões e histórico de alterações de design |
| `docs/mapa-georreferenciado.md` | Filtros, JS e estrutura do Mapa |
| `docs/financiamento-climatico.md` | Painel de Financiamento Climático |
| `docs/nota-pais.md` | Mapa-múndi Nota País e coalizão CHAMP |
| `CONTRIBUTING.md` | Workflow Git e padrões de código para contribuidores |
