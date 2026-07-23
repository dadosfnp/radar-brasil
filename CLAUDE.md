# CLAUDE.md — Contexto do Projeto Radar Brasil

> Arquivo de contexto para sessões com Claude Code. Atualizado ao final de cada expediente.
> Última atualização: 2026-07-23

---

## Visão Geral

**Radar Brasil** é uma plataforma Django para monitoramento do federalismo climático brasileiro. Permite avaliar, comparar e explorar dados climáticos de municípios em todo o território nacional. Desenvolvida pela FNP — Frente Nacional de Prefeitas e Prefeitos.

URL de produção: Render (branch `main`)
Branch de desenvolvimento ativo: `next`
Branch de feature atual: `feat/i18n-english`

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 6.0.1 · Python 3.10+ |
| API | Django REST Framework |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL via Render |
| Dados dinâmicos | gspread (Google Sheets) · pandas · openpyxl · xlrd |
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
    services/
      avaliacao_painel.py        ← Painel Multinível (fichas técnicas)
      painel_multinivel.py       ← scores/critérios por eixo
      financiamento_climatico.py ← tabela de financiamentos
      mapa_georreferenciado.py   ← dados do mapa Leaflet
  municipios/          ← views e urls principais
  api/                 ← DRF (pouco usado)
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
docs/
  CHANGELOG.md         ← histórico completo de alterações
  design.md            ← decisões e alterações de design
```

---

## Fontes de Dados — Google Sheets

Todos os serviços leem via `gspread` com cache em memória de **1800s (30 min)**. Reiniciar o servidor ou aguardar o TTL para ver novos dados.

| Serviço | Arquivo | Sheet ID | GID |
|---|---|---|---|
| `avaliacao_painel.py` | Fichas Técnicas | `16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8` | (worksheet "dados") |
| `avaliacao_painel.py` | Parâmetros | `1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE` | (worksheet "dados") |
| `painel_multinivel.py` | Parâmetros | `1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE` | (worksheet "dados") |
| `financiamento_climatico.py` | Financiamentos | `1sxKa2yu8GL8U6m4zoK42hO75a-YZqVKK5PKNJ8jlJ8c` | `793540087` |
| `mapa_georreferenciado.py` | Mapa | `1qMPAIB5e6IoG_cdCpBMIgzG8fZS1wUZ1zQbOFW3jACs` | `1619423236` |

**Colunas relevantes de `avaliacao_painel.py`:**
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

## Git — Fluxo de Trabalho

```
feature/nome  →  next  →  main (produção Render)
bugfix/nome   ↗
feat/i18n-english  ← branch atual de i18n EN
```

**Regras:**
- Nunca commitar diretamente em `next` ou `main`
- Sempre partir de `next` para criar branches de trabalho
- `main` só recebe via merge de `next`
- Branch `feat/i18n-english` é desenvolvimento — **não subir para produção ainda**

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
5. Branch `feat/i18n-english` é **somente desenvolvimento** — não fazer push para produção
6. Commits via PowerShell: usar variável `$msg = @'...'@` + `git commit -m $msg` para evitar problemas com acentos

---

## Estado Atual do Projeto (2026-07-23)

### Branch `feat/i18n-english` — i18n EN completo (LOCAL, não publicado)

**O que foi feito:**
- Implementado seletor PT|EN no header (`base.html`)
- `LocaleMiddleware` + `LANGUAGES` + `LOCALE_PATHS` no `settings.py`
- `locale/en/LC_MESSAGES/django.po` com 243 strings traduzidas
- `static/js/i18n.js` com `DICT.en` cobrindo todos os módulos
- i18n aplicado em 9 templates + 5 arquivos JS
- Todos os textos restantes em PT traduzidos (auditoria completa)
- Fichas técnicas com hyperlinks nas palavras (`link_eixo`, `link_orgao`, `link_arcabouco`)
- CSS para links nas fichas (`color: inherit`, underline sutil, hover teal)
- `avaliacao_painel.py` refatorado para retornar `link_eixo` e `url` por campo
- Serviços atualizados para novos Google Sheets (5 fontes)

**Commits no branch (locais):**
```
e3b847d feat: implementa tradução EN com seletor PT|EN no header
964113e feat: aplica i18n completo em toda a plataforma (9 templates + 5 JS)
020ea9f fix: adiciona 'Anterior', 'Próximo' e 'de' ao dicionário i18n.js
5309290 fix: traduz rodapé e aria-labels do menu hamburguer para EN
43d9be3 fix: traduz strings dinâmicas do Avaliação Painel Multinível no modo EN
+ commits de hyperlinks e novos Google Sheets
```

### Pendências

- **Banco de dados EN**: usuário mencionou possibilidade de fornecer URLs de Google Sheets em inglês para abastecer a versão EN da plataforma. Aguardando URLs.
- **Migração DigitalOcean** (standby): mover dados do Google Sheets para PostgreSQL DigitalOcean — pausado.

---

## Rotina de Final de Expediente

Quando o usuário sinalizar fim do dia:

1. Atualizar este arquivo (`CLAUDE.md`) com o estado atual do projeto
2. Verificar se `docs/CHANGELOG.md` e `docs/design.md` estão atualizados
3. Confirmar quais commits estão locais e quais foram publicados
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
