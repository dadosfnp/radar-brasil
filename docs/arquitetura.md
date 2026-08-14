# Arquitetura e Decisões — Radar Brasil

Documento vivo com a arquitetura escolhida, o histórico de decisões e as pendências em aberto.
Última atualização: 2026-07-27.

---

## 1. Arquitetura adotada: Django + PostgreSQL DigitalOcean + Render

Os dados de indicadores saíram do Google Sheets e passaram para um banco PostgreSQL
gerenciado (DigitalOcean `fnp-database`, database `radar_brasil`). A importação
(via `sync_sheets_db`) continua lendo as planilhas, mas é um comando administrativo
avulso — não parte do fluxo de requisição.

```
Google Sheets PT/EN  ←── sync_sheets_db (comando de importação, não é do fluxo de req)
                              │ gspread + pandas
                              ▼
               PostgreSQL DigitalOcean (fnp-database / radar_brasil)
                  RegistroFicha · RegistroParametro
                  RegistroFinanciamento · RegistroMapa
                              │ Django ORM
                              ▼
            Django Services  (apps/indicadores/services/)
             avaliacao_painel    painel_multinivel
             financiamento_climatico    mapa_georreferenciado
                              │  JSON para o frontend
                              ▼
                      Django Views
                        ├── render() → Templates HTML (server-side)
                        └── JsonResponse → APIs para o JS do painel
                                   │
                                   ▼
                        Vanilla JS (sem bundler, sem build)
                         Leaflet · Plotly · html2canvas
                         └── i18n.js (RBi18n) — strings dinâmicas PT↔EN
                                   │
                                   ▼
                            Navegador (Render)
```

### Por que este desenho

- **PostgreSQL como banco de indicadores:** consultas são instantâneas (sem latência de API),
  sem dependência de quota/throttling do gspread, sem cache em memória com TTL.
- **Importação explícita via comando:** a equipe editorial atualiza as planilhas e depois
  um admin roda `python manage.py sync_sheets_db` para sincronizar. Processo deliberado
  (não automático), que garante revisão antes de atualizar produção.
- **Django server-side rendering:** templates renderizados no servidor eliminam a necessidade
  de um frontend separado (Next.js, SPA). APIs JSON complementam para os componentes
  interativos (mapa, gráficos, fichas).
- **Sem bundler no JS:** um arquivo por página, carregados diretamente pelo template.
  Elimina Node.js da cadeia de deploy e simplifica manutenção por equipe pequena.
- **Render como hosting:** deploy automático via push no remoto `prod`, SSL nativo.
- **Dois registros por idioma (PT + EN):** cada model tem campo `lang` ("pt"/"en").
  O conteúdo EN não é tradução automática — a equipe mantém planilhas independentes.

---

## 2. Serviços e fluxo de dados

### Módulos de serviço

| Módulo | Função | Sheets lidas |
|---|---|---|
| `avaliacao_painel.py` | Fichas técnicas por estrutura — campos, links, descrições, nível | Fichas PT + EN · Parâmetros PT + EN |
| `painel_multinivel.py` | Scores agregados por critério e eixo nos 4 eixos do Painel | Parâmetros PT + EN |
| `financiamento_climatico.py` | Tabela de financiamentos + 3 gráficos (Setor, Origem, Ente) | Financiamento PT + EN |
| `mapa_georreferenciado.py` | Dados dos municípios para o mapa Leaflet | Mapa PT + EN |

### Componentes e custos

| Componente | Onde roda | Custo |
|---|---|---|
| Dados de indicadores (PT e EN) | PostgreSQL DigitalOcean (`radar_brasil`) | DigitalOcean cluster compartilhado |
| Importação de dados | `sync_sheets_db` (gspread + pandas, on-demand) | Grátis |
| Backend / templates / APIs JSON | Django 6.0 no Render | Render Starter |
| Banco de autenticação | PostgreSQL via Render | Render Starter |
| Estáticos (CSS, JS, imagens) | WhiteNoise (embutido no Django) | Grátis |
| CI · lint · testes | GitHub Actions (origin/radar-brasil) | Grátis |

### Normalização EN → PT nos services

As sheets EN têm cabeçalhos e valores em inglês. Cada service aplica um pipeline antes de servir os dados:

1. `df.rename(columns=_EN_COLS)` — mapeia nomes de colunas EN → PT internos
2. `df["Eixo"].replace(_EN_EIXO)` — normaliza valores do eixo (ex.: "Governance" → "Governanca")
3. Regex `Level N → Nível N` na coluna Nível (revertido na saída quando `lang == "en"`)
4. `_EN_CRITERIO` — mapeamento de nomes de critérios EN → PT usado exclusivamente para ordenação em `ORDEM_CRITERIOS`

---

## 3. Deploy e infraestrutura

O projeto usa **dois remotos Git** com papéis distintos:

| Remoto | Repositório | Papel |
|---|---|---|
| `origin` | `brunofnp/radar-brasil` | CI via GitHub Actions (flake8 · black · pytest) |
| `prod` | `dadosfnp/radar-brasil` | Deploy automático no Render — este remoto é monitorado |

**Crítico:** push apenas em `origin` não aciona o Render. Produção exige push nos dois remotos:

```powershell
git push origin main
git push prod main
```

### Pipeline de CI (GitHub Actions)

1. `flake8 apps setup` — lint Python (max-line-length=100)
2. `black apps setup --check` — formatação Python
3. `pytest apps/indicadores/tests.py -v` — 13 testes de integração

### Fluxo de branches

```
feature/nome  →  next  →  main
bugfix/nome   ↗           ↓
                  git push origin main
                  git push prod main
                         ↓
                    Render (produção)
```

Nunca commitar diretamente em `next` ou `main`. Branches de trabalho partem sempre de `next`.

---

## 4. Sistema i18n PT/EN

A internacionalização opera em duas camadas independentes:

| Camada | Mecanismo | Escopo |
|---|---|---|
| Templates Django | `LocaleMiddleware` + `{% trans %}` + `django.po` | 243 strings estáticas dos templates HTML |
| Strings JS dinâmicas | `RBi18n.t()` em `i18n.js` | Labels de gráficos, tooltips, mensagens geradas pelo JS |
| Dados dos indicadores | Sheets separadas por idioma + normalização EN→PT nos services | Conteúdo editorial — fichas, critérios, financiamentos, mapa |

**Problema conhecido — encoding NFC/NFD:** strings com `ã`, `ç` etc. podem falhar no lookup do dicionário JS por discrepância de normalização Unicode entre arquivos. Solução aplicada: dicts paralelos com chaves ASCII onde necessário (ex.: `EIXO_LABELS_EN` em `avaliacao-painel.js`).

---

## 5. Histórico de decisões

### Adotadas

**Django sobre Flask / FastAPI**
Necessidade de admin, autenticação, i18n nativa e sistema de templates num projeto de equipe pequena. Django entregava tudo sem bibliotecas adicionais.

**Google Sheets como banco de indicadores**
A equipe editorial da FNP já opera em planilhas. Migrar os indicadores para um banco relacional exigiria uma interface de administração customizada ou treinamento no Django Admin — custo de UX sem benefício proporcional. O Django possui banco relacional apenas para autenticação.

**Cache em memória (sem Redis)**
Volume de acessos pequeno, servidor único no Render. Redis adicionaria custo mensal e complexidade operacional sem ganho real para o perfil de uso. Cache em memória com TTL de 30 min é suficiente e reinicia junto com o processo.

**Dois remotos Git com papéis distintos**
CI roda em `origin` (brunofnp — GitHub Actions gratuito); deploy via `prod` (dadosfnp — monitorado pelo Render). Separação de responsabilidades permite CI no repo pessoal sem expor o pipeline ao repo da organização.

**JS vanilla sem bundler**
Equipe pequena, sem necessidade de reatividade complexa. Um arquivo por página, carregado via `<script>` no template. Elimina Node.js e etapa de build do pipeline de deploy.

**WhiteNoise em vez de S3 / CDN**
Volume de estáticos pequeno e previsível. WhiteNoise serve com compressão Brotli e cache headers nativamente no mesmo processo Django, sem custo adicional e sem adicionar um serviço externo ao stack.

**Duas camadas de tradução + sheets separadas por idioma**
O conteúdo EN não é tradução mecânica das planilhas PT — a equipe mantém dois conjuntos editoriais independentes. A camada Django cobre templates; `RBi18n` custom cobre strings geradas em JS (impossível via `.po`).

### Descartadas

**Next.js / SPA como frontend separado**
Exigiria API REST completa no backend, build step de Node.js no deploy e gestão de dois repos ou um monorepo. O custo de complexidade superava o benefício para o perfil de uso (conteúdo majoritariamente estático com alguns componentes interativos).

**Migração dos indicadores para PostgreSQL DigitalOcean** *(foi adotada)*
Implementada em 2026-08-14 via `feature/migracao-postgresql`. Os benefícios (consultas SQL, sem latência da API gspread, sem TTL de cache) justificaram o esforço. Ver seção "Adotadas" acima.

---

## 6. Estado atual

**Branch ativo:** `next` — limpo, sincronizado com `origin/next` e `prod/main`

### O que está no ar

- Seletor PT|EN no header — `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS`
- 243 strings de template traduzidas (`django.po` + `django.mo` compilado)
- `i18n.js` (RBi18n) cobrindo strings dinâmicas em todos os módulos JS
- 5 Google Sheets EN com cache por idioma nos 4 services
- Normalização EN→PT de colunas, eixos, critérios e níveis nos services
- Fichas técnicas com hyperlinks (`link_eixo`, `link_orgao`, `link_arcabouco`)
- Exibição "Level N" nos gráficos e tabelas EN
- Campo Composição com quebras de linha normalizadas (PT e EN)
- Gráfico "Resource Transfers by Government Level" com labels traduzidos (State/Municipal)
- Ordem das barras do Painel Multinível EN idêntica à PT nos 4 eixos

---

## 7. Pendências e próximos passos

### Corrigir divergência next/main (aguardando autorização)

O `main` acumulou commits de merge que o `next` não tem, impedindo fast-forward e fazendo o Render exibir "Merge branch 'next'" no histórico de deploys em vez do nome real do commit.

Fix: force push em ambos os remotos para alinhar `main` ao tip de `next`:

```powershell
git push origin next:main --force-with-lease
git push prod next:main --force-with-lease
```

Após isso, usar `git push origin next:main` + `git push prod next:main` diretamente (sem merge local).

### Popular o banco PostgreSQL (`sync_sheets_db`)

A migration `0001_initial.py` cria as tabelas. Após fazer o deploy com `DATABASE_URL`
apontando para o DigitalOcean, rodar:

```
python manage.py migrate
python manage.py sync_sheets_db
```

O comando importa as 8 planilhas (4 PT + 4 EN). Repetir sempre que os dados das
planilhas forem atualizados pela equipe editorial.
