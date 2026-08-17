# CLAUDE.md — Contexto do Projeto Radar Brasil

> Arquivo de contexto para sessões com Claude Code. Atualizado ao final de cada expediente.
> Última atualização: 2026-08-17 (fim do dia)

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
- Arquivo PO: `locale/en/LC_MESSAGES/django.po` (243 strings)
- Compilar: `python manage.py compilemessages` ou script `compile_po.py`

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

## Estado Atual do Projeto (2026-08-17 — fim do dia)

### Branch atual: `main` — em produção no DigitalOcean

**Commits do dia (nova identidade visual):**

```
d2f2653 merge: next -> main (nova identidade visual #264584)
83ca5e5 merge: nova identidade visual (paleta navy/azul #264584)
ea60064 style: aplica nova identidade visual Radar Brasil (paleta navy/azul #264584)
92f915e docs: atualiza CLAUDE.md com contexto completo pos-deploy DigitalOcean
```

### Nova Identidade Visual — aplicada

**Paleta de cores substituída:**
- `--color-primary`: `#264584` (azul de referência da marca FNP)
- `--color-bg-page`: `#d9e8f5` (azul claro — fundo de todas as páginas)
- Todos os tons teal/verde eliminados (exceto bolinhas piscantes em `#22c55e`)
- Degradês removidos — cor sólida `#264584` em cabeçalhos e botões

**Logos e avatares atualizados (`static/img/`):**
- `logo-radar-fundo-escuro.svg` — header (fundo navy)
- `logo-radar-fundo-claro.svg` — backgrounds claros
- `logo-radar-negativo-monocromatico.svg` / `logo-radar-positivo-monocromatico.svg`
- `avatar-principal.svg` / `avatar-positivo.svg` / `avatar-negativo.svg`
- `logo-radar.svg` removido

**Arquivos modificados:** 13 CSS, 4 JS, `base.html`, `docs/CHANGELOG.md`, `docs/design.md`

### Remotos — estado atual

| Remoto | URL | `next` | `main` |
|---|---|---|---|
| `origin` | `brunofnp/radar-brasil` | ✅ atualizado | ✅ atualizado |
| `prod` | `dadosfnp/radar-brasil` | ✅ criado hoje | ✅ atualizado |

### Infraestrutura de produção

| Item | Valor |
|---|---|
| Droplet | `fnp-web` — Ubuntu 24.04 — `root@142.93.205.222` |
| App dir | `/opt/radar-brasil/` |
| Porta interna | `127.0.0.1:8005` |
| Domínio | `https://radarbrasil.fnp.org.br` |
| SSL | Let's Encrypt via certbot (expira 2026-11-15) |
| Banco | `fnp-database` (DigitalOcean Managed PostgreSQL 18) — database `radar_brasil`, user `radarbrasil` |
| Container | `radarbrasil` — Python 3.12-slim, Gunicorn 3 workers |

### Arquitetura de dados

```
Google Sheets → sync_sheets_db → PostgreSQL → App (Django ORM)
```

- Runtime **nunca** acessa Google Sheets diretamente
- `python manage.py sync_sheets_db` repovoa o banco a partir das planilhas
- Rodar novamente quando as planilhas forem atualizadas

**Contagem atual no banco:**

| Tabela | PT | EN |
|---|---|---|
| RegistroFicha | 98 | 98 |
| RegistroParametro | 412 | 412 |
| RegistroFinanciamento | 46 | 46 |
| RegistroMapa | 2322 | 2322 |

### Rotina de deploy de atualizações

```powershell
# Local (após commits em main)
git push origin main
git push prod main

# Droplet (SSH)
cd /opt/radar-brasil
git pull
docker compose build
docker compose up -d
```

Para atualizar dados das planilhas (sem redeploy):
```bash
docker compose exec radarbrasil python manage.py sync_sheets_db
```

### i18n EN — completo

- Seletor PT|EN no header, `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS`
- `locale/en/LC_MESSAGES/django.po` com 243 strings + `django.mo` compilado
- `static/js/i18n.js` com `DICT.en` cobrindo todos os módulos
- i18n aplicado em 9 templates + 5 arquivos JS
- Banco EN populado (fichas, parâmetros, financiamento, mapa)

### Pendências

- **Deploy no droplet:** push feito, falta rodar no servidor:
  ```bash
  cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
  ```
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
