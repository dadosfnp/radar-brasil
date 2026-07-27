# CLAUDE.md — Contexto do Projeto Radar Brasil

> Arquivo de contexto para sessões com Claude Code. Atualizado ao final de cada expediente.
> Última atualização: 2026-07-27

---

## Visão Geral

**Radar Brasil** é uma plataforma Django para monitoramento do federalismo climático brasileiro. Permite avaliar, comparar e explorar dados climáticos de municípios em todo o território nacional. Desenvolvida pela FNP — Frente Nacional de Prefeitas e Prefeitos.

URL de produção: Render (branch `main` do remoto `prod`)
Branch de desenvolvimento ativo: `next`

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 6.0.1 · Python 3.10+ |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL via Render |
| Dados dinâmicos | gspread (Google Sheets) · pandas |
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

## Git — Remotos

O projeto tem **dois remotos**:

| Remoto | URL | Uso |
|---|---|---|
| `origin` | `https://github.com/brunofnp/radar-brasil.git` | Repositório pessoal — CI GitHub Actions |
| `prod` | `https://github.com/dadosfnp/radar-brasil.git` | Repositório da organização FNP — **Render monitora este** |

**CRÍTICO:** Para subir para produção é obrigatório fazer push nos dois:
```powershell
git push origin main
git push prod main
```
Fazer push só em `origin` NÃO aciona o deploy no Render.

---

## Fontes de Dados — Google Sheets

Todos os serviços leem via `gspread` com cache em memória de **1800s (30 min)**. Reiniciar o servidor ou aguardar o TTL para ver novos dados. Cada serviço tem cache separado por idioma (`{"pt": ..., "en": ...}`).

### Sheets PT

| Serviço | Sheet ID | GID / worksheet |
|---|---|---|
| `avaliacao_painel.py` — Fichas | `16s59h5uE0R6GZTkrjQZI152gUOjfjxeOeAwy7v6JYH8` | worksheet "dados" |
| `avaliacao_painel.py` — Parâmetros | `1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE` | worksheet "dados" |
| `painel_multinivel.py` — Parâmetros | `1jKGDhsjDYHRKEJCLdP-5zCxCSh5q5A5t8x1RhErmEoE` | worksheet "dados" |
| `financiamento_climatico.py` | `1sxKa2yu8GL8U6m4zoK42hO75a-YZqVKK5PKNJ8jlJ8c` | GID `793540087` |
| `mapa_georreferenciado.py` | `1qMPAIB5e6IoG_cdCpBMIgzG8fZS1wUZ1zQbOFW3jACs` | GID `1619423236` |

### Sheets EN

| Serviço | Sheet ID | GID |
|---|---|---|
| `avaliacao_painel.py` — Fichas EN | `1EkaWJ2n391vXukwsNTGj-RMd65S55hADtR24lxRXx9g` | `1400373985` |
| `avaliacao_painel.py` — Parâmetros EN | `1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8` | `1708988989` |
| `painel_multinivel.py` — Parâmetros EN | `1t-ivtzjEbn4qneUZr9vaRwCgq7iGKTmIHUnM0aBp4f8` | `1708988989` |
| `financiamento_climatico.py` EN | `1bQoDf4AEElaNy6_vUQSh-tOoZDKZA-R7mEn2eUmZEmk` | `449650871` |
| `mapa_georreferenciado.py` EN | `1uj_8PdAvTScqxSGi0ujBCRhiuJgXXFeaZFO8B4qJtqk` | primeira aba |

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

### Normalização EN → PT nos services

Sheets EN têm cabeçalhos e valores em inglês. Cada service aplica:
1. `df.rename(columns=_EN_COLS)` — mapeia nomes de colunas EN → PT
2. `df["Eixo"].replace(_EN_EIXO)` — mapeia valores do eixo EN → PT
3. Regex `Level N → Nível N` na coluna Nível
4. Na camada de saída, converte de volta: `nivel.replace("Nível ", "Level ")` quando `lang == "en"`

**Quebras de linha em campos de texto (fichas técnicas):**
- Backend (`get_ficha`): normaliza `\r\n` e `\r` → `\n` em todos os valores de campo
- Frontend (`avaliacao-painel.js`): converte `\n` → `<br>` explicitamente ao montar o HTML

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
                        Render (produção)
```

**Regras:**
- Nunca commitar diretamente em `next` ou `main`
- Sempre partir de `next` para criar branches de trabalho
- `main` só recebe via merge de `next`
- Ao subir para produção: `git push origin main` **E** `git push prod main`

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

## Estado Atual do Projeto (2026-07-24)

### Branch atual: `next` — limpo, sincronizado com `origin/next` e `prod/main`

**Commits recentes (HEAD):**

```
bcda73c fix: garante ordem das barras EN identica ao PT no Painel Multinivel
fab14e4 fix: traduz labels Estadual/Municipal no grafico de repasse por ente em EN
5de85ce docs: atualiza CLAUDE.md com estado atual (2026-07-23 fim do dia)
8a6a2df fix: detecta e separa itens concatenados no campo Composicao da ficha EN
840f78a docs: atualiza CLAUDE.md com estado atual do projeto (2026-07-23)
3e8e773 fix: corrige quebras de linha no campo Composicao da ficha tecnica EN
```

**i18n EN completo em produção** — tudo mergeado e publicado em `origin` e `prod`:
- Seletor PT|EN no header, `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS`
- `locale/en/LC_MESSAGES/django.po` com 243 strings + `django.mo` compilado
- `static/js/i18n.js` com `DICT.en` cobrindo todos os módulos
- i18n aplicado em 9 templates + 5 arquivos JS
- Fichas técnicas com hyperlinks (`link_eixo`, `link_orgao`, `link_arcabouco`)
- Banco de dados EN: 5 Google Sheets em inglês com cache por idioma
- Normalização EN→PT de colunas e valores nos 4 services
- Labels de ficha técnica em inglês no modo EN (`_CAMPOS_LABELS`)
- Exibição "Level N" (em vez de "Nível N") nos gráficos e tabelas EN
- Filtro correto de campos "Does not apply" no modo EN
- Quebras de linha normalizadas no campo Composição das fichas (PT e EN)
- Heurística de split para itens concatenados sem separador na sheet EN (`re.sub` minúscula→maiúscula)

**Fixes EN pós-lançamento (2026-07-24):**
- Gráfico "Resource Transfers by Government Level": labels `Estadual`/`Municipal` traduzidos para `State`/`Municipal` no modo EN (`financiamento_climatico.py`)
- Painel Multinível: ordem das barras EN agora idêntica à PT nos 4 eixos — adicionado `_EN_CRITERIO` em `painel_multinivel.py` mapeando nomes de critérios EN → PT para lookup em `ORDEM_CRITERIOS`

**Limpeza incorporada:**
- 17 arquivos removidos (template órfão, asgi.py, 15 imagens)
- `rest_framework` removido de `INSTALLED_APPS` e `requirements.txt`
- `print()` convertidos para `logger` em `painel_multinivel.py`

### Normalização EN → PT nos services — detalhe `painel_multinivel.py`

`_EN_CRITERIO` mapeia nomes de critérios EN → PT **apenas para fins de ordenação** (não altera os labels exibidos). Critérios sem mapeamento (`Financing`, `Representation of Gender, Race and Ethnicity`) ficam ao final, espelhando o comportamento PT (onde `Financiamento` e `Representação de Gênero, Raça e Etnia` também não batem nos nomes renomeados de `ORDEM_CRITERIOS`).

### Divergência `next` / `main` — problema cosmético pendente

O `main` acumulou commits de merge ("Merge branch 'next'") que o `next` não tem. Isso:
- Impede `git merge --ff-only next` (fast-forward)
- Faz o Render exibir o nome do merge commit no histórico de deploys em vez do nome real do commit

**Fix planejado (requer autorização do usuário):** force push em `main` nos dois remotos para apontar para o mesmo commit do `next`:
```
git push origin next:main --force-with-lease
git push prod next:main --force-with-lease
```
Após isso, sempre usar `git push origin next:main` + `git push prod next:main` direto (sem merge local).

**Workaround atual:** usar `git merge next -m "<mensagem descritiva>"` para que o Render exiba algo útil.

### Pendências

- **Divergência next/main**: corrigir com force push em `main` — aguardando autorização do usuário
- **Migração DigitalOcean** (standby): mover dados do Google Sheets para PostgreSQL DigitalOcean — pausado, aguardando decisão

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
