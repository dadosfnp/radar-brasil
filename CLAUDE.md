# CLAUDE.md — Contexto do Projeto Radar Brasil

> Arquivo de contexto para sessões com Claude Code. Atualizado ao final de cada expediente.
> Última atualização: 2026-11-18 (fim do expediente)

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
    models.py          ← RegistroFicha, RegistroParametro, RegistroFinanciamento, RegistroMapa, TraducaoCache
    services/
      avaliacao_painel.py        ← Painel Multinível (fichas técnicas) — lê do ORM
      painel_multinivel.py       ← scores/critérios por eixo — lê do ORM
      financiamento_climatico.py ← tabela de financiamentos — lê do ORM
      mapa_georreferenciado.py   ← dados do mapa Leaflet — lê do ORM
      sheets_reader.py           ← lê Google Sheets — usado APENAS pelo sync_sheets_db
      traducao.py                ← traduz PT→EN/ES via Gemini (Fichas/Parâmetros) — usado APENAS pelo sync_sheets_db
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

## Backup antes de merge/deploy em produção

**Regra:** antes de mesclar uma branch grande em `next`/`main` e subir pro droplet, criar tags de backup apontando pro estado atual de `main` e `next` nos dois remotos — assim dá pra reverter exatamente pro que estava em produção se algo der errado depois do deploy.

```powershell
# 1. Conferir o commit atual de cada remoto/branch (git remote -v mostra "prod" como "nucleo" localmente neste repo)
git fetch origin; git fetch prod
git rev-parse origin/main prod/main origin/next prod/next

# 2. Criar uma tag anotada por estado distinto (datar no nome, ex.: backup-main-2026-11-17)
git tag -a backup-main-AAAA-MM-DD <commit-do-main> -m "Backup de main/producao antes do merge de <branch>"
git tag -a backup-next-AAAA-MM-DD <commit-do-next> -m "Backup de next antes do merge de <branch>"

# 3. Publicar as tags nos remotos onde esse commit existe (origin e/ou prod)
git push origin backup-main-AAAA-MM-DD backup-next-AAAA-MM-DD
git push prod backup-main-AAAA-MM-DD
```

- Se `main`/`next` estiverem no mesmo commit nos dois remotos, uma tag só já cobre os dois — não duplicar.
- Se `next` estiver divergente entre `origin` e `prod` (ex.: commits ainda não propagados pra organização), criar uma tag por estado distinto e publicar cada uma só onde aquele commit existe.
- Pra reverter em caso de problema: `git checkout backup-main-AAAA-MM-DD` (ou mover `main`/`next` de volta pra essa tag com `git reset --hard`/`git push --force-with-lease`, sempre confirmando com o usuário antes).
- Tags não são apagadas depois — ficam como histórico de pontos de restauração.

---

## Fontes de Dados — Google Sheets → PostgreSQL

O runtime **não acessa** o Google Sheets. Os dados ficam no PostgreSQL e são atualizados via:

```bash
docker compose exec radarbrasil python manage.py sync_sheets_db
```

O comando lê as planilhas abaixo, normaliza os dados e faz `bulk_create` no banco (apaga e reinsere por idioma).

**Rodando local no Windows (fora do Docker, pra popular o SQLite de dev):** `.venv\Scripts\python manage.py sync_sheets_db` quebra com `UnicodeEncodeError` no `cp1252` padrao do console (as mensagens do comando usam "→"). Rodar com `$env:PYTHONIOENCODING='utf-8'` antes no PowerShell (ou `PYTHONIOENCODING=utf-8` no bash). Credenciais ja existem em `.secrets/fnp-radar-sheets.json` (`GOOGLE_SHEETS_CREDENTIALS` no `.env` local).

### Planilhas PT

**Mudança 2026-11-18:** Fichas e Parâmetros PT passaram a viver numa única planilha combinada ("V01_BANCO DE DADOS_2025", e-mail Paulo Diego) em vez de 2 planilhas separadas. As abas `Saida_fichas`/`Saida_parametros` são preenchidas automaticamente pela própria planilha (fórmulas internas, várias abas de trabalho `GOVERNANÇA`/`POLÍTICAS E PLANOS`/`PROGRAMAS`/`LINHAS_FINANCIAMENTO`/`Catalogo`/etc. — não lidas pelo nosso código) e preservam exatamente as mesmas colunas que as planilhas antigas (conferido coluna a coluna, incluindo o erro de digitação histórico "Classsificacao"). Há também um arquivo separado "C1/C01_BANCO DE DADOS_2025" que é só material de trabalho/legenda da equipe de dados (explica como as colunas brutas viram as variáveis finais) — não é lido pelo nosso código.

| Tabela | Sheet ID | GID / worksheet |
|---|---|---|
| Fichas | `10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic` | worksheet "Saida_fichas" |
| Parâmetros | `10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic` (mesma planilha) | worksheet "Saida_parametros" |
| Financiamento Climático | `10bQF-i3AzELKGFBgWNqRgdC6aLUbekNpg4Rl5kPX2Ic` (mesma planilha, achado em 2026-11-18) | worksheet "Financiamento_climatico" |
| Mapa Georreferenciado | `1qMPAIB5e6IoG_cdCpBMIgzG8fZS1wUZ1zQbOFW3jACs` | GID `1619423236` |

**Pegadinha de nome (achada em 2026-11-18):** a planilha do Mapa Georreferenciado (`1qMPAIB5e6IoG...jACs`) se chama **"Financiamento"** no título do arquivo no Google Drive — não tem nenhuma relação com a tabela "Financiamento Climático" (que é outra coisa, migrada pro V01 acima). É só coincidência de nome de quem criou o arquivo. Confundiu uma sessão inteira até o usuário mandar print do Drive mostrando o nome do arquivo. **Nunca inferir o conteúdo de uma planilha pelo nome do arquivo — conferir sempre o header da aba.**

### Tradução automática (Fichas, Parâmetros e Financiamento Climático) / Mapa segue com planilha EN própria

**Mudança 2026-11-18 (implementada e verificada):** Fichas, Parâmetros e Financiamento Climático deixaram de ter planilha EN própria — a equipe de dados só mantém o PT (as 3 agora na mesma planilha V01), e o `sync_sheets_db` gera EN e ES automaticamente via Gemini a partir do conteúdo PT (`apps/indicadores/services/traducao.py`), com cache em `TraducaoCache` (migração `0002_traducaocache`) por hash do texto pra não retraduzir conteúdo inalterado a cada sync. Só o Mapa continua com planilha EN mantida à mão, sem ES ainda (`--lang es` pula só essa sheet com aviso, não erro).

- **Campos nunca traduzidos** (ficam na forma canônica PT em qualquer idioma): `eixo` (chave normalizada), `nivel` ("Nível N"), os 3 campos de link. `avaliacao`/`criterio` (nome do critério, ex. "Operacionalidade") usa vocabulário fixo de 12 valores (`CRITERIO_EN`/`CRITERIO_ES` em `traducao.py`) em vez de tradução livre, pra nunca divergir dos dicionários já existentes em `painel_multinivel.py` (`_EN_CRITERIO`/`_ES_CRITERIO`). Os 10 campos do Financiamento Climático (`programa`, `setor`, `modalidade`, `origem`, `valor`, `contrapartida`, `federal`, `estadual`, `municipal`, `ente`) traduzem livremente — nenhum é chave de lookup em outro lugar do código. Todo o resto (descrição, órgão responsável, arcabouço normativo, etc.) traduz via Gemini, em lote de até 40/50 textos únicos por chamada, com 3 modelos de fallback (`GEMINI_TRADUCAO_MODELS`, variável própria — **não** reaproveita `GEMINI_MODELS` do Assistente de propósito, pra um `.env` que já define uma não sobrescrever a outra silenciosamente) e timeout próprio (`GEMINI_TRADUCAO_TIMEOUT_S`, padrão 60s — mais longo que o do Assistente porque sync roda offline).
- **Nunca cachear uma tradução que falhou:** se todos os modelos falharem num lote, o texto em PT é usado como stand-in só naquela execução — nunca gravado em `TraducaoCache`, pra uma próxima tentativa poder chamar o Gemini de novo em vez de ficar presa num "sucesso" falso (bug encontrado e corrigido nesta sessão, 210 entradas erradas já tinham sido gravadas antes do fix).
- **Cuidado com formatação de moeda traduzida:** o espanhol reformata "R$ 0,00" como "0,00 R$" (símbolo depois do número) — `_has_ente_value()` em `financiamento_climatico.py` usava um conjunto fixo de strings pra detectar "valor zero" e não reconhecia essa ordem, tratando um repasse zerado como se tivesse valor no filtro "Nível de Governo" em espanhol. Reescrito pra confiar no valor numérico (`_parse_num`) sempre que o texto tem algum dígito, independente de formatação/idioma — só cai no "é texto descritivo, conta como valor" quando não há nenhum dígito.
- Testado de ponta a ponta com a planilha V01 real: Fichas (100 registros, 21 campos), Parâmetros (434 registros, 9 campos) e Financiamento Climático (49 registros, 10 campos) PT/EN/ES, qualidade conferida manualmente — só identidades esperadas entre idiomas (números, siglas, nomes próprios de bancos/programas, cognatos PT/ES).
- **Drive-by fix:** campo `ente` (= "Tipo do repasse/financiamento" na planilha) sempre voltava vazio desde sempre — o código procurava pelas colunas "Ente"/"Ente Federado", que nunca existiram na planilha (nome real da coluna é outro). Corrigido a busca da coluna; hoje o valor real da planilha é sempre "Valores indisponíveis" (dado ainda não preenchido pela equipe), mas pelo menos chega ao banco.

| Tabela | Sheet ID | GID |
|---|---|---|
| Mapa EN | `1uj_8PdAvTScqxSGi0ujBCRhiuJgXXFeaZFO8B4qJtqk` | primeira aba |

**Credenciais:** `GOOGLE_SHEETS_CREDS_JSON` no `.env` do droplet (JSON da service account em linha única). Arquivo local: `.secrets/fnp-radar-sheets.json`.

**Colunas relevantes (fichas):**
- `Link_eixo` — URL do eixo (usado no título da ficha técnica)
- `Link_orgao` — URL do órgão responsável
- `Link_arcabouco` — URL do arcabouço normativo

**Critérios renomeados (`painel_multinivel.py` + `avaliacao_painel.py` — `_CRITERIO_DISPLAY_PT`):**
- `Sustentabilidade Financeira` (era "Financiamento") — **somente no eixo Governança**; Políticas e Planos e Programas exibem "Financiamento"
- `Diversidade e Representatividade` (era "Representação de Gênero, Raça e Etnia") — todos os eixos
- `Monitoramento e Avaliação` (era "Monitoramento e Participação Local") — todos os eixos

**Regra do rename condicional:** `fin_key = "Financing" if lang == "en" else "Financiamento"` removido do `display_map` quando `eixo_front != "Governanca"`. Aplicado em `dados_para_grafico` e `get_tabela`.

**Correção de mojibake (2026-09-23):** algumas células das planilhas foram coladas com encoding errado (UTF-8 lido como Latin-1 — ex.: "São Luís" virou "SÃ£o LuÃ­s", "Seleções" virou "SeleÃ§Ãµes"). `sheets_reader.py` aplica `_corrigir_mojibake()` em toda célula de texto lida (nos 3 pontos de leitura: `_ler`, `ler_financiamento`, `ler_mapa`) — só mexe em texto com os marcadores 'Ã'/'Â' e só troca se o round-trip `encode('latin-1').decode('utf-8')` for válido (texto limpo, incluindo maiúsculas legítimas como "PAVIMENTAÇÃO", nunca é alterado). **Ampliada em 2026-10-23:** a versao antiga so tratava 'Ã'/'Â' e a celula inteira, e deixava passar pontuacao corrompida ('â€“' = '–', 'â€™' = '’', 'â€‹' = espaco invisivel) nos dados EN do Mapa e do Financiamento. Agora corrige trecho a trecho (regex de byte inicial UTF-8 + continuacoes lidas como Latin-1 ou cp1252, convertendo so o que forma UTF-8 valido) e remove U+200B; acento legitimo na mesma celula nao e afetado. Teste em `apps/indicadores/tests.py` (`CorrigirMojibakeTest`). Varredura de producao (paginas + APIs, PT e EN): script `varre_acentos.py` no scratchpad da sessao. Isso corrige automaticamente a cada `sync_sheets_db`, mas **não corrige dados já salvos** — é preciso rodar `sync_sheets_db` de novo (reimporta e substitui por idioma) para sanear os registros existentes no banco.

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

## Templates — pegadinha do comentário `{# #}` (achado 2026-11-16)

**Comentário Django `{# ... #}` não suporta múltiplas linhas.** Se `{#` e `#}` ficam em linhas diferentes, o Django não reconhece como tag nenhuma — o texto inteiro (chaves incluídas) vaza como texto literal visível na página renderizada (confirmado com `Template(...).render()`; não dá erro, só renderiza errado). Isso já aconteceu 3x nesta sessão (`painel-multinivel.html`, `landing.html`, `_federalismo_triangle.html`) e só foi pego porque o usuário testou no navegador de verdade.

**Regra:** comentário Django de uma linha só, sempre (`{# comentário curto #}`). Para comentário de várias linhas, usar a block tag `{% comment %}...{% endcomment %}` (essa sim suporta multilinha) — mas nunca escrever o nome literal de outra tag Django (`{% endcomment %}`, `{% endblock %}` etc.) dentro de um comentário `{# #}` por perto: já quebrou o parser antes (`TemplateSyntaxError`) nesta mesma sessão.

---

## CI — GitHub Actions

Arquivo: `.github/workflows/ci.yml`

Roda em push para `next` e `main` (remoto `origin`):
1. `flake8 apps setup` — lint Python (max-line-length=100, config em `.flake8`)
2. `black apps setup --check` — formatação Python
3. `pytest apps -v --tb=short`: 48 testes (indicadores + assistente)

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

## Skills recomendadas neste projeto

| Skill | Quando usar aqui |
|---|---|
| `frontend-ui-engineering` | Quase todo trabalho é CSS/template. Testar PT **e** EN (strings EN são mais longas) e os breakpoints do header (1600/1440/1300/1180/1080/980/900) + 768/480 |
| `browser-testing-with-devtools` | Conferir layout real antes de commitar CSS (historicamente feito com Playwright). Exige o MCP chrome-devtools configurado |
| `git-workflow-and-versioning` | Branch a partir de `next`, CHANGELOG no mesmo commit, push em `origin` **e** `prod` |
| `code-review-and-quality` / `ponytail-review` | Antes do merge `next` → `main` |
| `security-and-hardening` | Ao mexer em `sync_sheets_db`/`sheets_reader` (credenciais da service account) ou em links vindos das planilhas (validação `startswith("http")`) |
| `performance-optimization` | Imagens de `static/img/` (fotos da Metodologia/Sobre têm 4 a 9 MB cada) |
| `shipping-and-launch` | Deploy no droplet: `build` obrigatório para estáticos, `compilemessages` após mudar `.po`, `sync_sheets_db` após fix em leitura de dados |
| `graphify` | Perguntas de arquitetura: grafo em `graphify-out/` (não versionado). Atualizar com `/graphify . --update` |

Particularidades que um agente precisa saber (detalhes nas seções acima):

- Runtime lê só do ORM; Google Sheets só via `sync_sheets_db`. Nunca importar `sheets_reader` em services/views.
- Testes: `apps/indicadores/tests.py` e `apps/assistente/tests.py` (pytest + pytest-django, `conftest.py` mocka o gspread; o Gemini e mockado nos testes). CI roda flake8 + black `--check` + pytest.
- Cache-buster `?v=N` no template: incrementar ao alterar qualquer CSS/JS e atualizar a tabela de versões.
- Prefixo de classe CSS por página (`.ap-`, `.mg-`, `.fc-`, `.np-`, `.pm-`); JS vanilla, um arquivo por página, strings via `RBi18n.t()`.

---

## Estado Atual do Projeto (2026-11-18)

### Branch atual: `main` (local e os dois remotos identicos, ver abaixo)

**Deploy completo em producao em 2026-11-18** (commit final `eabcb3a`): novo banco PT Fichas/Parametros/Financiamento Climatico (planilha V01) com traducao automatica EN/ES via Gemini, espanhol na interface inteira, seletor de idioma redesenhado, e o fix do Assistente (ver "Incidente" na secao do Assistente). `sync_sheets_db` rodado em producao com sucesso: Fichas (100), Parametros (434) e Financiamento (49) em PT/EN/ES. Confirmado com testes reais na API de producao (Financiamento, Painel, Assistente respondendo certo) e visualmente pelo usuario.

Durante o proprio deploy, `financiamento [pt]` quebrou em producao (`value too long for type character varying(500)` — ver "79a rodada" no CHANGELOG) e deixou a tabela vazia por alguns minutos ate o hotfix (campos viram `TextField`) ser publicado e o `sync_sheets_db --sheet financiamento` rodado de novo. Resolvido no mesmo dia.

**3 fixes pos-deploy, achados pelo usuario testando em producao (todos resolvidos e publicados no mesmo dia):**
1. Badge "Nivel 5" ilegivel em espanhol (texto escuro sobre fundo escuro) — CSS so cobria PT/EN
2. Total do Mapa Georreferenciado 3,4x maior em EN/ES que em PT (R$ 633bi vs R$ 185,9bi) — `mapa_georreferenciado.py` comparava `perfil` com uma string fixa em portugues; achado pre-existente, nao introduzido nesta sessao
3. Painel ▸ Visão Geral no mobile: bolhas de eixo empilhando em 2 linhas desbalanceadas + barrinha de score comprimida — CSS sem tratamento mobile adequado

**Historico do dia anterior (2026-11-17), para contexto:** a reestruturacao completa (menu em cascata, mapas consolidados, Painel com acordeao, Landing redesenhada) foi mesclada e publicada em `035a2a6`; achado principal daquele dia foi o **Cloudflare** cacheando `nota-pais.js`/`i18n.js` por ate 1 ano (ver "Infraestrutura de producao").

### Remotos

| Remoto | `next` | `main` |
|---|---|---|
| `origin` (brunofnp) | `eabcb3a` | `eabcb3a` |
| `nucleo` (dadosfnp) | `eabcb3a` | `eabcb3a` |

> `main` e `next` identicos nos dois remotos, sem commits pendentes de push. **Nota:** o remoto da organizacao esta configurado localmente como `nucleo` (`git remote -v`) — "prod" usado em documentacao antiga era so o nome conceitual.

**Tags de backup criadas antes do merge (2026-11-17):** `backup-main-2026-11-17` (aponta pro `9d39b38`, a producao antes desta reestruturacao) publicada em `origin` e `nucleo`; `backup-next-2026-11-17` (aponta pro `342833f`, o `next` do `origin` antes do merge, com o fallback do Gemini que ainda nao estava no `nucleo`) publicada so em `origin`. Ver secao "Backup antes de merge/deploy em producao" para o procedimento.

### Git — autenticacao configurada

Remotos com PAT no `.git/config` (config apenas local, nao versionada). Desde 2026-10-19 sao **dois tokens diferentes**, ambos classic com escopos `repo` + `workflow` (sem `workflow` o GitHub recusa push que altere `.github/workflows/ci.yml`):
- `origin`: token da conta **brunofnp** (o repo `brunofnp/radar-brasil` e privado; token de outra conta responde "Repository not found")
- `prod`: token da conta **dadosfnp**

Remoto extra `pessoal` (`devBrunoMarra/radar-brasil`) existe no config local, sem uso no fluxo.

### SSH — alias configurado

`~/.ssh/config` com alias `fnp-web`:
```
Host fnp-web
    HostName 142.93.205.222
    User root
    IdentityFile ~/.ssh/id_ed25519_fnp_web
```
Claude nao consegue SSH no droplet diretamente — o usuario deve rodar os comandos de deploy no proprio terminal.

### Droplet — estado atual

Deploy do Assistente em 2026-10-19/20. `.env` do droplet tem `GEMINI_API_KEY` (so foi salva de fato em 2026-10-20: o chat respondia 'indisponivel' porque a linha nao existia; conferir com `docker compose exec radarbrasil sh -c 'echo ${#GEMINI_API_KEY}'`, deve dar 53), `GEMINI_TIMEOUT_S=35` e `ASSISTENTE_ORCAMENTO_S=45` (paliativo: o Gemini gratuito chega a 17s so para responder 'ok' nos picos; respostas levam ate ~46s). Mudanca no `.env` exige `docker compose up -d --force-recreate`. O usuario roda os comandos direto no terminal ja aberto no droplet (nao precisa do wrapper `ssh fnp-web "..."` quando ja esta conectado):
```bash
cd /opt/radar-brasil && git pull && docker compose build && docker compose up -d
```

**CRITICO:** `docker compose up -d` sem `build` nao atualiza arquivos estaticos (WhiteNoise serve de dentro da imagem). Sempre rodar `build` apos mudancas em CSS/JS/templates.

**Apos mudancas em `sheets_reader.py`/`sync_sheets_db.py` (ou qualquer fix que precise reprocessar dados ja importados):** o deploy sozinho so atualiza o codigo. Tambem rodar `docker compose exec radarbrasil python manage.py sync_sheets_db` para reimportar as planilhas e substituir os registros existentes no banco com a correcao aplicada — feito em 2026-09-23 para o fix de mojibake.

### Infraestrutura de producao

| Item | Valor |
|---|---|
| Droplet | `fnp-web` — Ubuntu 24.04 — `root@142.93.205.222` |
| App dir | `/opt/radar-brasil/` |
| Porta interna | `127.0.0.1:8005` |
| Dominio | `https://radarbrasil.fnp.org.br` |
| SSL | Let's Encrypt via certbot (expira 2026-11-15) |
| CDN | **Cloudflare** na frente do dominio (confirmado em 2026-11-17 via headers HTTP — `Server: cloudflare`, `cf-cache-status`). Nao estava documentado aqui antes |
| Banco | `fnp-database` (DigitalOcean Managed PostgreSQL 18) — database `radar_brasil`, user `radarbrasil` |
| Container | `radarbrasil` — Python 3.12-slim, Gunicorn 3 workers |

**CRITICO — cache do Cloudflare (achado 2026-11-17):** todo arquivo estatico serve com `Cache-Control: public, max-age=31536000, immutable` (WhiteNoise). Sem um `?v=N` no template, a URL nunca muda — o Cloudflare guarda a mesma resposta em cache por ate 1 ano e **nenhum** rebuild/redeploy no droplet troca o que o navegador recebe, porque o Cloudflare fica na frente da origem e nem chega a reconsultar o droplet. `static/js/nota-pais.js` e `static/js/i18n.js` eram os 2 unicos arquivos JS/CSS referenciados em qualquer template sem `?v=` (confirmado por grep em todo `templates/`+`base_templates/`) — ficaram servindo copias de setembro/2026 (confirmado via header `Last-Modified`) mesmo depois do codigo already corrigido no repo e deployado. Corrigido adicionando `?v=1` aos dois. **Regra:** todo `<script src="{% static ... %}">` e `<link ... {% static ... %}>` de arquivo proprio (nao CDN externo) tem que ter `?v=N` sem excecao — nunca assumir que um arquivo "estavel" (tipo um helper global como i18n.js) pode ficar sem, porque o Cloudflare nao faz distincao.

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

### Header Global — estado (2026-11-18)

CSS: `static/css/base.css` **v=28** | Template: `base_templates/base.html`

**Seletor de idioma (v26-v28, substitui a pilula PT|EN antiga):** dropdown bandeira+nome+seta, 3 idiomas (Português/English/Español). Desktop: `.rb-lang-select` ao lado do logo FNP, mesmo componente visual dos dropdowns Sobre/Painel (fundo navy `#0d1640`, abre no hover/focus-within); posicionado com `.rb-lang-select { position: absolute; bottom: -26px; right: 16px }` — **mesmo valor usado pela pilula antiga**, bottom (nao top) pra ficar sempre abaixo do logo FNP sem invadi-lo nem escapar do header sticky. Mobile: item dentro do painel do hamburguer, classe `.rb-nav-item--lang-mobile` com `display: none` por padrao e só `display: block` dentro do breakpoint `<=900px` — **sem isso ele vaza como uma aba a mais no desktop**. Bandeiras sao SVG proprio em `static/img/flags/{br,gb,es}.svg` (nao emoji — emoji de bandeira nao renderiza no Windows/Chrome, cai pro fallback de texto "BR"/"GB").

**Cuidado ao mexer no CSS deste seletor:** `.rb-lang-form` e `.rb-lang-select` sao as DUAS classes do MESMO elemento no HTML (`<div class="rb-lang-form rb-lang-select">`). Ja aconteceu (2026-11-18, v27→v28) de cada classe ter sua propria regra de `position` (uma `absolute`, outra `relative`) — mesma especificidade, vence quem vem depois no arquivo, e `relative` venceu por acidente, fazendo o pill virar item do flex ao lado do logo (em vez de sair do fluxo) e o `bottom: -26px` ser aplicado sobre essa posicao errada, sobrepondo o logo. **Toda declaracao de `position`/`top`/`bottom`/`left`/`right` deste elemento tem que viver numa regra so** (hoje em `.rb-lang-select`) — nunca dividir entre as duas classes torcendo pra uma "ganhar" na cascata. Confirmar qualquer mudanca aqui medindo com Playwright (`npx playwright`, ja usado localmente nesta sessao) antes de considerar resolvido — a screenshot sozinha enganou numa das tentativas (parecia certo, mas so porque o crop cortava antes de mostrar a sobreposicao).

**Fix v24 — fonte do menu aumentada:** desde a reestruturacao de 2026-11-16 o menu tem so 4 itens (Sobre/Nível País/Painel/Mapa, antes eram 7) — sobrava espaco e a fonte ficou pequena. Base subiu de `1.051rem` para `1.25rem`; os 6 degraus do nav fluido (ver Fix v20 abaixo) escalados na mesma proporcao (~1.19x).

**Fix v20 — nav desktop fluido (menu quebrava linha em notebooks):** com fonte cheia os 7 itens do menu so cabem em uma linha a partir de ~1570px de largura efetiva. Uma primeira tentativa (v19) estendeu o breakpoint do hamburger de `<=768px` para `<=1600px`, mas isso fazia notebooks comuns (1366/1440/1600px) mostrarem o menu hamburger mobile em vez do menu desktop — **rejeitado pelo usuario**: "quero que a versao desktop fique como versao desktop... nao colocar o sanduiche do mobile como solucao".

**Solucao final (v20):** fonte/padding dos nav-links e altura das logos encolhem em 6 degraus conforme a tela estreita, mantendo sempre o menu completo em uma linha (nav desktop de verdade):

| max-width | fonte do link | padding-x | logo Radar | logo FNP |
|---|---|---|---|---|
| (base) >1600px | 1.051rem | 18px | 74px | 62px |
| 1600px | 0.95rem | 14px | 68px | 56px |
| 1440px | 0.875rem | 12px | 64px | 52px |
| 1300px | 0.8125rem | 10px | 58px | 48px |
| 1180px | 0.75rem | 8px | 52px | 42px |
| 1080px | 0.6875rem | 6px | 46px | 38px |
| 980px | 0.625rem | 5px | 42px | 34px |

Cada degrau foi encontrado empiricamente com Playwright (menor fonte que ainda cabe em uma linha em cada largura). Abaixo de **900px** nem 10px de fonte cabe mais — so ai colapsa para hamburger (janela estreita/tablet, nao notebook real), igual ao padrao mobile ja existente em `<=768px`.

**Regra geral daqui pra frente: hamburger e so para telas realmente estreitas (<900px, tablet/mobile). Se o menu nao couber em um notebook, a solucao e adicionar um degrau de encolhimento fluido (fonte/padding/logos), nunca esconder o menu atras de um hamburger em largura de notebook.**

**Gap acima do header (v15):**
- `body.rb-body::before { position: fixed; top: 0; height: 20px; background: var(--color-header-bg); z-index: 1000; pointer-events: none }` — cobre gap de renderizacao acima do sticky header com navy; nao afeta landing (usa `.lp-body`).
- `html { background: var(--color-header-bg) url(fundo-bg.png) ... }` — navy como cor fallback do html.

Layout grid 3 colunas `auto 1fr auto` em linha unica, sticky no topo:
- Coluna esquerda: logo Radar Brasil SVG `logo-radar-fundo-escuro.svg`, `height: 74px` desktop / `68px` mobile (v18 — era 62px; +20% de aumento), `?v=2` cache-buster no src do SVG
- Coluna central: `<nav class="rb-main-nav">` — links brancos `rgba(255,255,255,0.78)`, fonte `1.051rem`, active com `border-bottom: 2px solid #fff`
- Coluna direita: logo FNP `height: 62px` desktop / `34px` mobile + seletor de idioma; logos alinhados pelo topo (axis to axis, v17)

**Menu — item renomeado (2026-09-09):**
- "Nota Pais" renomeado para "Nivel Pais" em PT (`{% trans "Nível País" %}`)
- EN: "Country Level" (ja existia no django.po)

**Idioma no mobile (desde o redesign do seletor):** `.rb-lang-form` (pill desktop) fica `display: none` a partir de `<=900px` — nesse breakpoint o idioma vira um item a mais dentro do painel do hamburguer (`.rb-nav-item--lang-mobile`), sanfona embutida igual Sobre/Painel, nao mais um pill separado ao lado do logo FNP.

**Nav mobile (hamburger):**
- `.rb-nav-links` em mobile: `position: absolute; top: 100%; left: 0; right: 0` — dropdown full-width abaixo do header
- JS (`base.html`): `setNavOpen(open)` — eleva `.rb-header-wrapper` para `z-index: 2300` ao abrir (acima de sidebars z-index: 2100); reseta ao fechar
- Fecha ao clicar fora: `document.addEventListener('click', function(e) { if (!hdr.contains(e.target)) setNavOpen(false); })`
- Barras do hamburger: `background: rgba(255,255,255,0.85)` (era `var(--hdr-700)` = `#101d4f` = invisivel)

**Rodape mobile:**
- `.rb-footer-landing { display: none }` em `<=768px` — removido de todas as paginas no mobile

**Altura do header mobile:** ~88px (wrapper 6+6px + header-top 4+4px + logo 68px)

Nav visivel em TODAS as paginas inclusive landing.

### Assistente de dados (RAG): estado (2026-10-19, em producao)

App `apps/assistente/` | CSS `static/css/assistente.css` v=6 | JS `static/js/assistente.js` v=5 | Template `templates/assistente/_widget.html` (incluido no `base.html`, substitui o antigo botao "voltar ao topo")

- Arquitetura enxuta (sem banco vetorial): contexto completo por idioma (~50k tokens, 174 fontes: FAQ P1-P9 do `sobre.html`, secoes das paginas S1-S21, fichas F1-F98, financiamentos L1-L46) + ferramenta `consultar_mapa` sobre os 2.322 empreendimentos do Novo PAC. Respostas com citacoes `[F12]`/`[P3]`/`[S4]`/`[L5]`/`[MAPA]` (listas como `[F11, F29]` tambem sao reconhecidas)
- Paginas como fontes (`contexto.PAGINAS`): Nivel Pais, Metodologia, Sobre (sem o FAQ), Inicio e Landing, lidas do template renderizado em PT e EN e cortadas em cada h1-h3. Editar a pagina (ou recompilar o `.mo`) atualiza o assistente sozinho. E a unica fonte do Nivel Pais (Brasil 2025 = 3), que nao existe no banco
- Divergencia conhecida: a tabela do Nivel Eixo na Metodologia diz Politicas e Planos 17 e Linhas de Financiamento 17; o banco e o Fact Sheet tem 18 e 30 (98 no total). O prompt manda preferir as fichas para contagens. **Fica mais visivel desde 2026-11-16/17:** o Painel ▸ Visão Geral e os cards de eixo da Landing agora mostram a contagem do banco (18/30) — se alguem comparar com a tabela da Metodologia (17/17), vai notar a mesma divergencia ja documentada aqui, nao e um bug novo
- Gemini via `google-genai`, **plano gratuito** (~20 req/dia por modelo, ~60 perguntas/dia somando as reservas). Modelos em `GEMINI_MODELS` (padrao `gemini-3.5-flash,gemini-3.1-flash-lite,gemini-3.1-flash-lite-preview` — **mudou em 2026-11-18**, ver "Incidente" abaixo); SDK sem retries, timeout 15s por chamada e 25s por pergunta; modelo sem cota (429) e pulado ate a cota voltar
- **Incidente (2026-11-18): Assistente indisponivel em producao por horas.** Causa dupla: (1) `gemini-3-flash` (3a reserva desde 2026-10-21) nunca existiu na API (404 sempre, confirmado via `client.models.list()` — o Assistente rodava com so 2 reservas reais, nao 3, desde entao); (2) no mesmo dia, uma rodada de traducao em lote local (617 strings do `django.po` + reimportacao do Financiamento Climatico, ambos via Gemini) esgotou a cota diaria gratuita (20 req/dia) de `gemini-3.5-flash` — **mesma conta/chave Gemini usada em producao**, sem separacao entre dev local e producao (usuario so tem a conta geral da FNP, decidiu nao criar conta pessoal separada so pra isso). Com a 1a reserva esgotada, a 2a (`gemini-3.1-flash-lite`) em 503 momentaneo, e a 3a sempre 404, as 3 falharam juntas e o Assistente voltou "indisponivel" pros visitantes. Corrigido o bug permanente: 3a reserva trocada por `gemini-3.1-flash-lite-preview` (testada e respondendo rapido em 2026-11-18, nunca testada/rejeitada neste projeto antes — ao contrario do `gemini-3.5-flash-lite`, que ja tem historico documentado de travar 15-45s com o contexto completo do Assistente, entao NAO foi escolhida apesar de tambem estar disponivel). O esgotamento de cota em si so se resolve com o reset diario (~24h) — **pendencia comportamental, nao de codigo:** avisar antes de rodar qualquer traducao em lote grande via Gemini neste projeto, porque pode derrubar o Assistente em producao (ver memoria de sessao). **RESOLVIDO em producao (2026-11-18, mesmo dia):** o `.env` do droplet nunca definiu `GEMINI_MODELS` (achado ao diagnosticar — `echo $GEMINI_MODELS` dentro do container veio vazio), entao o Assistente sempre usou o default do codigo (`_PADRAO` em `servico.py`), que o deploy ja corrigiu sozinho, sem precisar editar `.env` nenhum. Confirmado com `python manage.py shell -c "from apps.assistente.servico import MODELOS; print(MODELOS)"` dentro do container (`['gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-3.1-flash-lite-preview']`) e com 3 perguntas reais de teste na API de producao, todas respondidas certo (1,6 a 8,5s, citando fontes)
- `InteracaoAssistente` grava pergunta/resposta/fontes/tokens/latencia; IP so como hash; respostas reaproveitadas para a mesma pergunta com os mesmos dados (nao gasta cota); 👍/👎 por resposta; admin so leitura em `/admin`
- Comandos: `avaliar_assistente` (golden set: FAQ + `golden_set.json`, confere fonte e numeros), `limpar_assistente` (retencao `ASSISTENTE_RETENCAO_DIAS`, padrao 90)
- DPO no widget: `mutiraobrasil@fnp.org.br`
- Mobile: tela cheia em celular (em pe e deitado), alvos 44px, campo 16px, "voltar" fecha o chat
- Plano pago recomendado para a gerencia (documentos fora do repo, em `04-Radar Brasil/`): Gemini 3.6 Flash com cache, ~US$ 189/mes no piloto (1.000 perguntas/dia) e ~US$ 784/mes na meta (4.800/dia); cobranca por uso, sem mensalidade minima; preco dobra em jan/2027

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

### Landing Page — estado (2026-11-17)

CSS: `static/css/landing.css` **v=16** | JS: `static/js/landing.js` **v=2** | Template: `templates/municipios/landing.html`

**Reestruturacao 2026-11-16 (quinta e ultima etapa da rodada dos especialistas):** hero antigo (iframe `mapa-brasil-hud.html`, grid 44/56%, card "Conhecimento em Acao" com chips Paineis/Mapas/Dados) **removido** — essas classes (`.lp-hero-inner`, `.lp-hero-right`, `.lp-info-card`, `.lp-hud-frame`) ficam orfas no CSS, sem uso. Nova hero (`.lp-hero--map`): mini-mapa Leaflet (mesmo padrao do Nivel Pais — GeoJSON Natural Earth, Brasil navy, resto cinza, bordas brancas) sem filtros/pins/interacao de zoom, so hover no Brasil mostra o badge da nota (ver Fix 2026-11-17 abaixo).

Depois da hero, 3 secoes:
- **"Por que avaliar o Federalismo Climatico?"**: triangulo Uniao/Estados/Municipios extraido para um partial reutilizavel `templates/municipios/_federalismo_triangle.html` (incluido aqui e em `sobre.html` — editar so la atualiza as duas paginas). Os 3 nos ganharam foto de fundo (shutterstock, overlay escurecido pra legibilidade).
- **"Os municipios estao na linha de frente..." (nova, 2026-11-17):** banner full-width com foto de fundo (shutterstock_2261699419, mesma do no "Municipios" do triangulo), entre a secao do triangulo e a de eixos — sem referencia visual exata, texto de apoio redigido com base no contexto do projeto, sujeito a ajuste.
- **"Eixos de avaliacao do Radar"**: 4 cards (Governanca/Politicas e Planos/Programas/Linhas de Financiamento), foto de fundo por eixo, descricao de uma linha e "Nivel Eixo X/5" — dados vindos do backend (`dados_para_grafico` em `apps/indicadores/services/painel_multinivel.py`, chamado em `apps/municipios/views.py::landing` pros 4 eixos; `eixos_resumo` no contexto).
- Sidebar "Sobre/Midia/Agenda" e a grade "Nossos Paineis" (4 cards) foram tiradas da pagina a pedido do usuario, mas em **stand-by**: o bloco inteiro (`.lp-content`) esta envolvido em `{% comment %}...{% endcomment %}` em `landing.html`, nao apagado — pra reativar, so tirar as duas tags.

**Fix 2026-11-17 (pedido do usuario):** linha divisoria abaixo do mapa (`border-top` da secao seguinte) removida; scrim branco atras do titulo/subtitulo removido (texto ganhou `text-shadow` branco em vez disso — nunca fica ilegivel, nem sobre o Brasil navy nem sobre o oceano branco); mapa recentralizado (`center:[-10,-62]`) pra empurrar o Brasil pra longe da area do texto. Badge da nota do Brasil (hover) agora usa as classes globais `.rb-brasil-badge-*` (`base.css`) com a nota em fonte grande — mesmo exato visual do mapa do Nivel Pais (ver `nota-pais.js`). Overlay das fotos dos cards de eixo trocado de navy pra preto neutro, menos azulado.

**Cuidado com imagem de fundo via `{% static %}` em producao:** o storage e `CompressedManifestStaticFilesStorage` (nomes com hash); nunca concatenar `{% static 'img/' %}{{ variavel }}` — isso ignora o hash e quebra em producao. Usar `{% static "img/"|add:variavel %}` (resolve o caminho inteiro de uma vez) ou, em JS puro (sem acesso a `{% static %}`), expor as URLs ja resolvidas via um objeto `window.*` escrito num `<script>` do proprio template (ver `EIXO_IMAGENS` em `painel-multinivel.html`) — nunca montar `/static/img/...` na mao no `.js`.

### Metodologia — estado (2026-09-17)

CSS: `static/css/metodologia.css` **v=53** | Template: `templates/municipios/metodologia.html`

**Hero mobile (v53):** em <= 900px o mapa HUD animado vira fundo do titulo/subtitulo (`opacity: .4`), em vez de sumir. Vale tambem para o Sobre (mesmo hero).

Hero padronizado com Inicio (mesma altura, badge, tipografia).

**Card Nota Metodologica (v43):**
- Card-link abaixo de "Para saber mais, acesse a nota metodologica."
- iframe com capa real do PDF `static/doc/Mutirão Brasil - Nota Metodológica 01 (Radar Brasil).pdf` escalado `scale(0.1344)` em container `80x113px` (proporcao A4)
- PDF atualizado em 2026-09-28 (versao revisada substituiu a anterior, commit `6b2120b`)
- iframe carregado via JS (`data-pdf`) para evitar problemas de encoding com o nome do arquivo
- Clique em qualquer ponto do card abre o PDF em nova aba (`target="_blank"`)
- Hover: `translateY(-2px)` + `box-shadow` + borda mais escura

**Formulas MathML (v41/v42):**
- Formulas renderizadas com `<math displaystyle="true"><mrow>...</mrow></math>` (horizontal, fracao em tamanho grande)
- Removido `display: block` do CSS (conflitava com flex container)
- Divisor sutil `border-top: 1.5px solid rgba(38,69,132,.12)` em `.meto-timeline-section` — separa scroll-stack de fotos da secao Historico do Federalismo

**Scroll-stack de fotos (v36 — estado atual — estilo Medellin):**

Layout: fundo transparente, sem faixa navy, foto como card flutuante com sombra.
Grid `.meto-scroll-sticky`: 58% fotos / 42% texto. `overflow: hidden` no sticky (clippa fotos ocultas mantendo sombra da foto visivel). `.meto-scroll-photos`: `overflow: visible`.

Ordem das fotos: clima(0) → sociedade(1) → natureza(2) → cidade(3)

Tag da foto: dark pill navy (`#101d4f`, branco, `border-radius: 999px`) — classe `.meto-scroll-tag`

JS — wheel handler ativo apenas sobre `.meto-scroll-photos` (nao a secao inteira):
- `photoProgress` (float irrestrito) — `initProg = 1/N` (primeira foto ja assentada ao entrar)
- `translateY(160%)` para fotos ocultas — necessario para ficarem abaixo do boundary do sticky (6vh top inset + 44vh altura + padding)
- Animacao de entrada: `rotate((1-p)*-6deg)` ao subir, straightens em `p=1`
- Loop bidirecional infinito sem frame branco: `displayProg = ((photoProgress - initProg) % 1 + 1) % 1 + initProg`
- PEEK = 26px — borda das fotos abaixo aparece apenas apos comecar a rolar (nao no estado inicial)
- Indicador de rolagem (2026-09-30, `sobre.css`): 4 bolinhas a esquerda da foto, a ativa vira pilula navy, sincronizado em `updateScrollPhotos()`; so desktop. Usuario prefere o estilo bolinha (tracos e contador+trilho foram rejeitados)
- Mobile `<=900px`: layout estatico (1 coluna, primeira foto visivel, secao `height: auto`)

**Timeline (v25 — sem alteracoes recentes):**
- Desktop: fundo `#fff`, bolha do ano circulo navy 56x56px, linha horizontal `rgba(38,69,132,.20)`.
- Mobile `<=600px`: ano como texto grande Sora 1.25rem bold em coluna de 66px; linha vertical tracejada.

**Secao de Calculo (v24):**
- Tres cards: Nivel Parcial, Nivel Eixo, Nivel Pais
- Formulas em fracao CSS + tabelas de referencia
- Nivel Pais: fundo gradient navy; grid 3col desktop / 1col mobile

**SVG piramide — bolinha flutuando (v25 fix):**
- Fix: `opacity="0"` inicial + `<animate attributeName="opacity" fill="freeze" to="0.80"/>` no begin.

### Nota Pais — estado (2026-11-17)

CSS: `static/css/nota-pais.css` **v=13** | Template: `templates/municipios/nota-pais.html`

**Reestruturacao 2026-11-16:** mapa (sidebar + Leaflet) agora vem ANTES do bloco `.np-intro` no HTML (antes era o contrario); texto do `.np-intro` reduzido (so contexto CHAMP + nota do Brasil + definicao + 3 etapas de calculo, sem "linha de base"/destaque/fechamento antigos). Essa pagina e a unica fonte de onde o Assistente extrai a nota do Brasil — qualquer edicao futura do texto deve manter "Nível País 3" em ordem de leitura (nao so dentro do badge visual), senao quebra `ContextoTest.test_paginas_da_plataforma_entram_como_fontes_nos_dois_idiomas`. Paleta do mapa consolidada com o Mapa Georreferenciado (oceano branco, ver "Identidade Visual").

**Fix 2026-11-17 (pedido do usuario):** nomes de pais escritos e pins vermelhos (`PIN_ICON`/`CHAMP_SIGNATORIES`) removidos do mapa em `nota-pais.js` — so cores + hover ficaram. Badge da nota do Brasil no hover agora usa as classes globais `.rb-brasil-badge-*` (`base.css`), com a nota em fonte grande — mesmo exato visual do mini-mapa da Landing (`landing.js`, `construirBadgeBrasil()`). **Nunca estilizar o badge so num dos dois lugares** — as classes sao globais de proposito, pra manter os dois mapas identicos.

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

### Mapa Georreferenciado — estado (2026-11-18)

CSS: `static/css/mapa-georreferenciado.css` **v=14** | JS: `static/js/mapa-georreferenciado.js` **v=7** | Template: `templates/municipios/mapa-georreferenciado.html`

**Fix total 3,4x maior em EN/ES (2026-11-18):** `mapa_georreferenciado.py` decidia a agregacao (Unico: minimo por municipio / Agrupado: uma vez por empreendimento) comparando `reg.perfil == "Investimento Único"` — string fixa em portugues. O campo `perfil` **nao e normalizado** pro PT na importacao (diferente de `eixo`) — a planilha EN grava o valor ja em ingles ("Single Investment"/"Pooled Investment"). Todo registro em ingles caia sempre no ramo "Agrupado" por engano, somando ao inves de pegar so o minimo por municipio — inflava o total de R$ 185,9bi (PT) pra R$ 633bi (EN/ES). Achado pre-existente (nao introduzido nesta sessao), corrigido comparando contra `{"Investimento Único", "Single Investment"}`. PT e EN agora dao o mesmo total exato.

**Basemap (2026-11-17, 2a tentativa):** CARTO Positron passou a exigir API key e quebrou em producao ("API KEY REQUIRED" sobre o mapa). 1a tentativa (OSM + filtro CSS `grayscale`) nao dava o branco/cinza exatos pedidos. **Solucao final: sem tile raster de terceiro nenhum.** `#mg-map` com `background: #fff` solido ("mar") + Brasil preenchido 100% solido `#B0BCC8` via GeoJSON ("continente"), mesma logica vetorial do Nivel Pais — cor exata garantida, zero dependencia de provedor externo. Perde o contexto de ruas/cidades do OSM (aceitavel: o conteudo real sao os marcadores de municipio, nao o basemap).

**Filtros (2026-11-17):** sidebar inteira (`.mg-sidebar`) convertida do tema escuro navy pro tema claro do Nivel Pais (mesmos valores literais: `#f5f8fa`/`#ccdde5`/`#1a3070` nos selects, `#334488` nos labels, etc.) — pedido explicito do usuario pra padronizar os dois mapas.

**Mapa mobile full-screen (mesmo padrao que Nota Pais):**
- Em `<=900px`:
  - `.mg-intro { display: none }` — removida em mobile
  - `.mg-page { padding: 0; gap: 0 }`
  - `.mg-layout { height: calc(100svh - 88px) }` — layout define o tamanho
  - `.mg-map-area { height: 100%; border-radius: 0 }` — preenche o layout pai
- Em `<=480px`: `height: calc(100svh - 76px)` com `border-radius: 0`

**Popup mobile — card overlay centralizado (v11/v12):**
- Em `<=900px`: popup Leaflet desabilitado (`display: none !important`); clique no marker abre `.mg-sheet` centralizado na tela
- `.mg-sheet`: `position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%) scale(0.90)` → escala para `scale(1)` ao abrir
- Animacao: `opacity + scale` com spring `cubic-bezier(.34,1.30,.64,1)` — sensacao de popup nativo
- Backdrop `rgba(10,20,60,.40)` fecha ao clicar; botao X fecha; clique no mapa fecha
- `max-height: 78vh` com scroll interno; `width: calc(100vw - 32px); max-width: 380px`
- Conteudo: mesmo `buildPopup()` do desktop (header navy, rows com icone/label/valor, lista de programas)
- `flex-wrap: nowrap` em `.mg-sheet-body .mg-popup-prog-meta` — badge de estagio e valor sempre na mesma linha
- Desktop: popup Leaflet nativo inalterado

**Autocomplete de municipio (v12/js v3-v4):**
- Dropdown `.mg-mun-suggestions` aparece a partir de 2 caracteres no campo Municipio
- Ate 8 sugestoes (nome + UF), priorizando "comeca com" antes de "contem"
- Normalizacao de acentos: `_normStr()` via `normalize('NFD')` — "sao" encontra "Sao Paulo"
- Sugestoes **contextuais**: `_getSuggestions()` le todos os filtros ativos (UF, Regiao, Porte, Eixo, Modalidade, Estagio, Executor) e aplica o mesmo criterio de `filtrar()` — selecionar AM mostra so municipios do AM
- Navegacao por teclado: seta cima/baixo, Enter confirma, Escape fecha
- Selecionar sugestao fecha o painel de filtros no mobile via evento `mg:filter-selected` (desacoplado do IIFE do template)
- Pressionar Enter sem sugestao selecionada tambem fecha o painel no mobile

**Sidebar/filtros mobile:**
- FAB `.mg-filter-fab` (bottom-left) abre sidebar como bottom sheet navy
- Fecha automaticamente ao selecionar qualquer filtro (select, checkbox) ou botao de acao
- Evento `mg:filter-selected` tambem fecha ao selecionar sugestao de municipio

### Painel Multinivel ("Visão Geral" no menu) — estado (2026-11-18, v4)

CSS: `static/css/painel-multinivel.css` v=24 | JS: `static/js/painel-multinivel.js` v=13 | Template: `templates/municipios/painel-multinivel.html`

**Fix mobile (2026-11-18):** bolhas de eixo quebravam em 2 linhas desbalanceadas (3+1) — viraram faixa de scroll horizontal numa linha só (`flex-wrap: nowrap; overflow-x: auto`), sem barra visível. Score do critério no mobile usava `width:100%; margin-left:28px` (margin soma fora da largura, estourava a linha e o flex-shrink comprimia a barrinha+label) — trocado por `padding-left:44px` (fica dentro do `width:100%`, `box-sizing:border-box` é global). Conferido com Playwright em 390px.

**Ajustes 2026-11-17:** bolhas de eixo agora ficam **sempre visiveis** desde o estado inicial "Visão geral" (antes so apareciam depois de abrir um eixo) — funcionam como atalho direto. Resumo do eixo + sua lista de criterios agora ficam dentro de um unico retangulo cinza (`.pm-eixo-expandido`, fundo `#f0f1f4`) que os abraca juntos — antes eram dois blocos soltos. Botao "Criterios e Parametros de Avaliacao" removido da Visão Geral (template/JS/CSS). Overlay das fotos dos cards recolhidos trocado de navy pra um preto neutro (`rgba(10,12,16,...)`), menos azulado.

**Correcao de fidelidade aos slides (2026-11-16, mesma sessao):** a primeira versao usava abas sempre visiveis (tabs classicas) — o usuario mandou slides mais detalhados mostrando um fluxo em 2 etapas: (1) estado inicial "Visão geral" com os 4 eixos recolhidos empilhados, foto de fundo, SEM bolhas de navegacao; (2) ao clicar em qualquer um, aparecem as bolhas (pilula laranja ativa / pilula pessego clara inativa) + só aquele eixo expandido (fundo cinza claro, sem foto) com seus criterios em cards NAVY (nome/descricao/peso/barrinha brancos sobre `var(--color-header-bg)`), nao mais cards brancos. KPI strip (Instancias Avaliadas/Eixos Analisados/Niveis de Avaliacao) e o header navy com label "Painel Multinível" **removidos** — nao apareciam em nenhum dos slides. Clicar na seta do resumo do eixo expandido volta pra visão geral (unica forma de "fechar" — nao estava nos slides mas e necessario, senao fica sem saida).
- JS: busca os 4 eixos em paralelo (`Promise.all`) pra popular a visão geral recolhida de uma vez; cache simples por eixo (`cacheEixos`) evita refetch ao reabrir
- Texto da explicacao do waffle trocado pra bater com a frase exata do slide ("Abaixo, cada célula corresponde a um componente avaliado neste critério...")
- `EIXO_COUNTS`/`atualizarKPI` (dict hardcoded de contagem por eixo) continuam removidos — o numero vem do banco via `total_componentes`

Grafico fixo em 380px. `_mostrarErroGrafico` esconde `#pm-chart-wrapper` no estado de erro.

**Fix overflow waffle no mobile (v17):**
- `min-width: 0` em `.pm-grid-container`, `.pm-grid-row`, `.pm-grid-cells`, `.pm-grid-ruler-cells`
- Sem isso, `min-width: auto` (default flex) forcava expansao para ~700px quebrando o layout
- `overflow: hidden` adicionado ao `.pm-chart-area` no mobile como barreira adicional

### Avaliacao Painel — estado (2026-11-18)

CSS: `static/css/avaliacao-painel.css` v=16 | JS: `static/js/avaliacao-painel.js` v=7 | Template: `templates/municipios/avaliacao-painel.html`

Todos os touch targets elevados para min-height: 44px em mobile.

**Fix badge "Nivel 5" ilegivel em espanhol (2026-11-18):** CSS so tinha `color:#ffffff` pros seletores `[data-nivel="Nível 5"]`/`"Level 5"` — faltava `"Nivel 5"` (ES, sem acento), entao o fundo verde-escuro inline (vem do backend) ficava com texto escuro padrao por cima, ilegivel. Adicionados os 6 niveis em espanhol em todas as regras de cor do badge; mesma causa corrigida na estrela de nivel maximo (`isMax` no JS).

**Fix modal ficha tecnica mobile (v14):**
- `inset: 88px 0 0` no `.ap-modal-overlay` em `<=900px` — overlay inicia abaixo do header
- Substituiu abordagem anterior de `padding-top: calc(88px + 8px)` que nao funcionava
- `.ap-modal-box { max-height: calc(100svh - 88px - 20px) }` — altura limitada ao espaco disponivel

**Fix z-index do modal desktop (v15):** `.ap-modal-overlay` tinha `z-index: 1000`, menor que `.rb-header-wrapper` (`z-index: 1001`) — o header sticky cobria o cabecalho colorido do modal (titulo, botao PDF, X) ao rolar a pagina em Componentes. Corrigido para `z-index: 1100`.

### Financiamento Climatico — estado (2026-09-11)

CSS: `static/css/financiamento-climatico.css` v=5 | JS: `static/js/financiamento-climatico.js` v=5 | Template: `templates/municipios/financiamento-climatico.html`

Componente MultiSelect com semantica `selected = new Set()` (vazio = todos ativos). Fix iOS mobile aplicado.
Tabela mobile: card layout com `td:first-child` como cabecalho navy.

**Filtros em cascata (v5 — 2026-09-11):**
- Endpoint GET `/indicadores/api/financiamento/filtros-disponiveis/` retorna opcoes validas para cada dimensao dado os outros filtros ativos
- `get_filtros_disponiveis()` no service: para cada dimensao, aplica os outros filtros e retorna valores distintos existentes
- `_has_ente_value()` extraida como funcao de modulo (usada em `_filtrar_ente` e `get_filtros_disponiveis`)
- `MultiSelect.updateAvailableOptions(newOpts)`: atualiza opcoes preservando selecoes validas; retorna true se removeu alguma
- `atualizarOpcoesDisponiveis()`: chama a API com debounce 150ms, atualiza dropdowns, re-aplica filtros se necessario
- Ao selecionar um programa, os demais filtros mostram apenas opcoes compativeis

**Filtro Nivel de Governo (2026-09-11):**
- `_filtrar_ente()` usa `_has_ente_value()` que detecta "R$ 0,00" como sem repasse
- Aplicado em `get_tabela()` e `get_graficos()` (afeta graficos e tabela)

### Identidade Visual

- `--color-primary`: `#264584` (navy FNP)
- `--color-bg-page`: `#ffffff` (fundo 100% branco, desde 2026-11-16 — era azul claro `#d9e8f5`)
- Background global: `#ffffff` solido no elemento `html` (via `base.css`); `fundo-bg.png` nao e mais usado em nenhum CSS (arquivo fica sem uso no repo)
- Body das paginas internas: `background: transparent` (mostra o branco do `html`); body de paginas com hero proprio: `background: #ffffff`
- Sem degrades, sem teal/verde (exceto bolinha piscante `#22c55e`)
- **Paleta consolidada dos mapas** (Nivel Pais + Mapa Georreferenciado): oceano branco, continente cinza `#B0BCC8`, Brasil navy `#264584`, fronteiras brancas — tokens `--map-ocean-color`/`--map-land-color`/`--map-brazil-color`/`--map-border-color` em `tokens.css`. Mapa Georreferenciado usa tile CARTO Positron sem rotulos (`light_nolabels`) no lugar do OSM colorido

### i18n — PT/EN/ES completo (2026-11-18)

- `LocaleMiddleware`, seletor com bandeira+nome+chevron no header (3 opcoes), `LANGUAGES = [("pt-br",...), ("en",...), ("es",...)]`
- `locale/en/LC_MESSAGES/django.po` (245+ strings) e `locale/es/LC_MESSAGES/django.po` (617 strings, traduzidas via Gemini em lote) — ambos com `.mo` compilado
- `static/js/i18n.js` — `RBi18n.t()` / `RBi18n.getLang()` — `DICT.en` e `DICT.es`
- Banco (producao, apos deploy de 2026-11-18): 100 fichas, 434 parametros e 49 financiamentos em PT/EN/ES; 2322 registros de mapa em PT/EN (sem ES ainda — `_lang_sem_es()` cai pro ingles)

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

### Versoes atuais dos CSS/JS (cache-busters nos templates)

| Arquivo | Versao no template |
|---|---|
| `base.css` | v=28 |
| `tokens.css` | v=3 |
| `inicio.css` | v=13 |
| `landing.css` | v=20 |
| `landing.js` | v=4 |
| `metodologia.css` | v=55 |
| `sobre.css` | v=27 |
| `avaliacao-painel.css` | v=16 |
| `avaliacao-painel.js` | v=7 |
| `painel-multinivel.css` | v=24 |
| `painel-multinivel.js` | v=13 |
| `mapa-georreferenciado.css` | v=14 |
| `mapa-georreferenciado.js` | v=7 |
| `financiamento-climatico.css` | v=5 |
| `financiamento-climatico.js` | v=5 |
| `nota-pais.css` | v=13 |
| `nota-pais.js` | v=2 (ganhou cache-buster em 2026-11-17; badge/mapa em 3 idiomas em 2026-11-18) |
| `linha-do-tempo.css` | v=1 |
| `components.css` | v=3 |
| `assistente.css` | v=6 |
| `assistente.js` | v=5 |
| `i18n.js` | v=2 (ganhou cache-buster em 2026-11-17; DICT.es em 2026-11-18) |

### Pendencias

Proximos passos:

- **Mapa Georreferenciado sem espanhol:** Fichas, Parametros e Financiamento Climatico ja tem ES de verdade (via Gemini); so o Mapa continua PT/EN (planilha EN mantida a mao, sem tradutor automatico) — `_lang_sem_es()` cai pro ingles em "es" pra esse dataset especifico, nunca devolve vazio. Migrar o Mapa pro mesmo padrao de traducao automatica fica pra uma proxima sessao, se fizer sentido
- **Gemini free tier — cota compartilhada entre dev local e producao (achado e combinado em 2026-11-18):** dev local e o Assistente em producao usam a mesma conta/chave Gemini (usuario nao tem conta separada, decidiu nao criar uma so pra isso). Uma rodada de traducao em lote pesada local pode esgotar a cota (20 req/dia por modelo) que a producao tambem usa — foi exatamente o que derrubou o Assistente por algumas horas nesta sessao (ver "Incidente" na secao do Assistente; resolvido no mesmo dia). **Combinado: avisar antes de rodar qualquer traducao em lote grande via Gemini neste projeto daqui pra frente** (ver memoria de sessao)
- **SEGURANCA (urgente):** os dois PATs do GitHub (`ghp_...`) apareceram em texto aberto numa saida de terminal colada no chat em 2026-10-20. Revogar nas contas brunofnp e dadosfnp, gerar novos (`repo` + `workflow`; `origin` = brunofnp, `prod` = dadosfnp) e limpar o historico do PowerShell

- **SEGURANCA (urgente):** chave privada da service account do Google Sheets (`radar-brasil-sheets@robust-charge-494120-s3`, key id `f40019d3`) esta no historico do repo **publico** `prod` (commit `5eecb76`, arquivo `.secrests/fnp-radar-sheets.json.json`). Apagar a chave no GCP, gerar outra para o `.env` do droplet, reduzir escopo para leitura; reescrever historico so com autorizacao
- **Assistente:** decisao da gerencia sobre o plano pago (apresentacao feita em 2026-10-19; documentos atualizados em 2026-10-20 com 51 mil tokens/pergunta: opcao C US$ 214 piloto, US$ 888 / R$ 4.794 meta; geradores no scratchpad da sessao: `planilha_ia.py`, `doc/gerar.js`, `doc/apresentacao.js`); plano gratuito oscila (503 de alta demanda) e e lento: so o pago resolve; melhorias opcionais oferecidas e nao feitas: aviso de espera apos ~10s e mensagem de erro 'alta demanda'; `createsuperuser` no droplet; cron do `limpar_assistente` (confirmar 90 dias com o DPO); especialistas definirem 20 a 30 perguntas para o `golden_set.json`
- **XSS armazenado (baixo risco, dados vem das planilhas internas):** `avaliacao-painel.js`, `financiamento-climatico.js` e `mapa-georreferenciado.js` montam HTML com texto das planilhas sem escapar

- **Fact Sheet (Sobre):** usuario vai trazer novas alteracoes na proxima sessao
- **Auditoria ponytail (nao aplicada, aguardando decisao):** decorador `@_api` para os 9 try/except das views, helper do dict de filtros do financiamento, `TemplateView` para as 8 views que so renderizam, trocar `oauth2client` (descontinuado) por `gspread.service_account_from_dict` (testar `sync_sheets_db` de verdade antes de subir), apagar `apps/municipios/templates/municipios/home.html` (orfao) e os `admin.py` vazios
- **Docs desatualizados:** `README.md`, `docs/arquitetura.md` e `docs/financiamento-climatico.md` ainda descrevem Render + leitura direta do Sheets + cache de 30 min (hoje: droplet + PostgreSQL)
- **CONSTRAINTS.md:** otimizar as 4 fotos da Metodologia (4 a 9 MB) — `fundo-bg.png` (930 KB) ficou sem uso em nenhum CSS desde a reestruturacao de 2026-11-16 (fundo do site virou branco solido), entao otimizar esse arquivo especifico deixou de fazer sentido (ele so ocupa espaco no repo); medir cobertura dos services (`pip install pytest-cov` no `.venv`) e fixar o limite
- **Opcional:** comparar os textos dos niveis 1 a 5 da Metodologia com o Anexo I do PDF publicado (formulas ja conferidas e coerentes)

**Resumo do dia (2026-11-18): novo banco PT + traducao automatica via Gemini (EN/ES), ainda local:**
- Mapeamento completo entre a planilha antiga e a nova "V01_BANCO DE DADOS_2025": `Saida_fichas`/`Saida_parametros` tem exatamente as mesmas colunas de sempre (conferido coluna a coluna) — zero trabalho de remapeamento, so trocar o Sheet ID (ja preparado ontem). Arquivo "C1/C01_BANCO DE DADOS_2025" e so material de trabalho da equipe de dados (nao lido pelo codigo)
- Acesso da conta de servico a planilha nova liberado pelo usuario; sync local rodado com sucesso (100 fichas, 434 parametros — antes eram 98/412)
- Construido o pipeline de traducao automatica PT->EN/ES via Gemini (`traducao.py` + `TraducaoCache`), substituindo as planilhas EN de Fichas/Parametros que a equipe de dados mantinha a mao. Dois bugs encontrados e corrigidos rodando de verdade (nao so com mock): cache gravando traducao falha como se fosse definitiva, e `resp.text` vindo `None` quebrando o parse; e um ajuste de qualidade (instrucao inicial mandava preservar "Decreto nº"/"Lei nº" por inteiro — corrigido pra traduzir as palavras e preservar so o numero)
- Espanhol adicionado como terceiro idioma do banco (Fichas/Parametros apenas por enquanto); Financiamento e Mapa continuam so PT/EN
- Achado a parte: `gemini-3-flash` (3a reserva do Assistente) nao existe na API (404) — Assistente em producao roda com so 2 reservas funcionais; nao corrigido (fora do escopo)
- **Continuacao do mesmo dia — seletor de idioma redesenhado e depois corrigido, espanhol completo na interface:** seletor PT|EN trocado por dropdown bandeira+nome+seta (commit `373972e`). Usuario reportou com prints 2 bugs visuais no resultado: item duplicado aparecendo como 5a aba no menu desktop, e o pill de verdade invadindo o logo FNP (mais bandeiras emoji aparecendo como texto "BR" no Windows/Chrome). Corrigido: item mobile só visivel `<=900px`, pill reposicionado com o valor historico (`bottom: -26px`), bandeiras trocadas por SVG proprio em `static/img/flags/`. Em seguida, espanhol completo na interface: `settings.LANGUAGES`, `locale/es/LC_MESSAGES/django.po` (617 strings traduzidas via Gemini em lote, revisadas, com retomada de progresso pra sobreviver a erros 503/429 do free tier), `DICT.es` no `i18n.js`, dicionarios ES em `painel_multinivel.py`/`avaliacao_painel.py`/`views.py`, e a 3a opcao "Español" no seletor. Mapa/Financiamento (sem banco ES) caem pro ingles em vez de vazio via `_lang_sem_es()`. 58 testes passando, conferido com dados reais em espanhol (Painel, Componentes, Landing)
- **Continuacao — Financiamento Climatico migrado + deploy completo em producao:** achado que Financiamento Climatico (nao so Fichas/Parametros) tambem migrou pra aba `Financiamento_climatico` do V01 (usuario perguntou se o banco novo cobria mesmo as 4 tabelas antigas — Mapa confirmado continuar na planilha de sempre, so com nome "Financiamento" por coincidencia no Drive, sem relacao). Migrado pro mesmo padrao PT+Gemini de Fichas/Parametros. Backup tag `backup-main-2026-11-18` criada antes do merge; `next`/`main` publicados nos dois remotos (commit final `eabcb3a`). Durante o `sync_sheets_db` em producao, `financiamento [pt]` quebrou (`origem` com 843 caracteres estourando `CharField(500)`) — hotfix rodando os 9 campos pra `TextField`, resync rodado de novo com sucesso. Assistente em producao testado e confirmado respondendo (ver "Incidente" acima). Depois do deploy, usuario achou mais 3 bugs visuais testando em producao (badge Nivel 5 ilegivel em ES, total do Mapa 3,4x maior em EN/ES, Painel mobile com bolhas empilhadas e score espremido) — todos corrigidos e publicados no mesmo dia (ver CHANGELOG 80a/81a/82a rodadas)

**Resumo do dia (2026-11-17): reestruturacao completa publicada (`035a2a6`), cache do Cloudflare descoberto:**
- Branch `feat/reestruturacao-menu-mapas-landing-painel` mesclada em `next` e `main` e publicada em `origin` + `nucleo`, depois de tags de backup do estado anterior
- Build do droplet quebrou por `msgid` duplicado no `django.po` ("Eixos de avaliação"/"Mapa", cadastrados duas vezes por descuido na sessao) — corrigido e republicado
- Ajustes pos-deploy pedidos pelo usuario: seta de dropdown removida dos eixos da Landing; bolhas de eixo do Painel trocadas de laranja/pessego pra azul/branco (depois invertidas a pedido — fundo azul, letras brancas em todas); fundo das secoes "linha de frente" e "Eixos de avaliação" da Landing trocado entre si pra fechar um retangulo branco que sobrava antes do rodape
- Varredura de todo `{% trans %}` dos templates contra o `django.po` achou 6 strings dos 3 cards "linha de frente" sem tradução EN (corrigido); achadas tambem (nao corrigidas, pre-existentes de setembro) 4 strings sem tradução em `sobre.html`
- Cores do Painel ▸ Visão Geral invertidas a pedido do usuario: retangulo do eixo passou de cinza pra navy, cards de criterio de navy pra cinza, com todas as cores de texto/acento adaptadas
- **Achado principal do dia:** usuario reportou que pins/nomes de pais no Nivel Pais e um texto nao traduzido no Painel continuavam em producao mesmo depois do codigo corrigido. Investigacao por `curl -I` (nao so inferencia do codigo) revelou que a producao fica atras do **Cloudflare** (nao documentado ate entao), que cacheava `nota-pais.js` e `i18n.js` por ate 1 ano — os 2 unicos arquivos JS/CSS do projeto inteiro sem `?v=N` no template. Corrigido adicionando `?v=1` aos dois; regra do cache-buster documentada como obrigatoria sem excecao
- E-mail da equipe de dados (Paulo Diego) pedindo troca da fonte de Fichas/Parametros PT pra uma planilha combinada nova — `sheets_reader.py` preparado localmente, bloqueado por falta de permissao da conta de servico na planilha nova (ver Pendencias)
- Mensagem de WhatsApp (sem termos tecnicos, com emoji de sirene) redigida pro usuario avisar o time sobre a atualizacao

**Resumo do dia (2026-10-20): Assistente com paginas como fontes (`b74d213`):**
- Producao: chave do Gemini nao estava no `.env` do droplet (corrigido); depois, instabilidade do plano gratuito (paliativo de timeout no `.env`)
- Icones de voto redesenhados e icone do assistente com o simbolo do Radar + estrelinha (`assistente.css` v=6)
- Paginas Nivel Pais, Metodologia, Sobre, Inicio e Landing viraram fontes `[S..]` (o Nivel Pais 3 so existe nelas); contexto ~50k tokens; citacoes em lista reconhecidas; 47 testes
- Tabela da Metodologia (17/17) mantida a pedido do usuario, apesar de divergir do banco (18/30)
- Calculo do Nivel Eixo/Pais pelo banco: na epoca, considerado inviavel sem o fator de relevancia (1 a 3) e o criterio prioritario nas planilhas. **Atualizado em 2026-11-16/17:** implementado mesmo assim em `dados_para_grafico` (media simples dos niveis medios de cada criterio, sem ponderacao — mesma formula de 3 etapas que o texto do Nivel Pais ja documenta publicamente) pra alimentar o Painel ▸ Visão Geral e os cards de eixo da Landing. Os valores computados (arredondados: Governanca 3, Politicas e Planos 3, Programas 3, Linhas de Financiamento 2) batem exatamente com os numeros que os proprios especialistas usaram no mockup original — e `total_componentes` (maior contagem por criterio) bate exatamente com 32/18/18/30 do Fact Sheet. Ainda e uma simplificacao (sem peso/fator de relevancia); se a metodologia oficial vier a exigir ponderacao, essa conta precisa ser revista.

**Resumo do periodo (2026-10-13 a 2026-10-19): Assistente de dados no ar (`916669a`):**
- App `apps/assistente` construido em 3 etapas (contexto, Gemini + API, widget), avaliador golden set (8/8 aprovadas), reaproveitamento de respostas, feedback, admin, retencao, latencia, compatibilidade mobile; 45 testes
- Revisao de seguranca da branch: limpa; achado fora da branch (chave da service account no historico publico) nas pendencias
- Documentos para a gerencia (planilha de opcoes, Word com planos, apresentacao do RAG) em `04-Radar Brasil/`, fora do repo
- Push em `origin` e `prod` exigiu tokens novos com escopo `workflow` (ver "Git — autenticacao configurada"); deploy no droplet com `GEMINI_API_KEY`

**Resumo do dia (2026-09-28): tudo deployado (`43bd8e9`):**
- PDF da Nota Metodologica substituido pela versao revisada (`6b2120b`); producao servindo o arquivo novo (3.626.606 bytes, conferido)
- Skills instaladas no usuario (ponytail, Agent Skills, graphify); secao "Skills recomendadas" neste arquivo
- `CONSTRAINTS.md` criado (imagens, testes, acessibilidade), so documento, sem CI
- Grafo graphify gerado em `graphify-out/` (ignorado no git); PDF entrou sem conteudo (falta `pypdf`)
- Auditoria ponytail rodada; achados listados nas pendencias acima

**Resumo do dia (2026-09-23) — 6 fixes, todos deployados:**
1. Modal ficha tecnica (Componentes): z-index atras do header ao rolar
2. Fact Sheet (Sobre): legenda do gauge descentralizada por animation + overflow horizontal fantasma
3. i18n EN: strings faltando no Fact Sheet e na intro do Nivel Pais
4. Header: menu quebrando linha em notebooks — 2 tentativas (v19 hamburger em 1600px foi **rejeitado pelo usuario**, v20 nav fluido com 6 degraus foi a solucao final)
5. Landing (EN): chips "Dashboards/Maps/Data" quebrando linha no card Knowledge in Action
6. Mojibake: encoding corrompido em textos do Google Sheets (Fichas/Parametros/Mapa, PT+EN) — corrigido na leitura + resync rodado em producao

Nota informativa (nao acionavel): DNS do `fnp.org.br` gerenciado em conta DigitalOcean separada ("Nucleo de Dados"). SSL expira 2026-11-15 (renovacao automatica via certbot).

### Pagina Sobre: estado (2026-09-30)

CSS: `static/css/sobre.css` **v=26** + `metodologia.css` **v=53** | Template: `templates/municipios/sobre.html`

Secoes em ordem:
1. Fact Sheet (sb-infographic): folha unica de 630px "Evolucao do Federalismo Climatico", ampliada 1.4x via `zoom` no desktop (>= 960px)
2. "Por que avaliar o Federalismo Climatico?" (meto-federalism-section)
3. Scroll-stack de 4 fotos (meto-scroll-section)
4. Historico do Federalismo Climatico (meto-timeline-section)
5. FAQ com accordion (sb-faq-section)

**Fact Sheet v26 (2026-09-30), estado atual:** detalhes em `docs/design.md`.
- Topo `.hero`: marca + botao, 3 info-cards (em fluxo, `min-height` 229px), card de avaliacao com gauge meio-donut em SVG inline (arcos vetoriais; `conic-gradient` serrilhava as divisas), fatias 32/18/18/30 em 180deg + legenda
- Bloco `.evolution`: grafico Nivel Pais por ano (2025 = 3) + barras de componentes 2025 (32/18/18/30) e 2026 ("em analise"), todos em SVG inline (nao voltar para `div` absolutas: desalinhava); rotulos de categoria em HTML alinhados por % do viewBox. Layout em cards brancos com sobretitulo/titulo/selo e notas de rodape ("Total: 98 componentes"); fundo navy `#161c4e` (paleta da antiga folha 02), cards `#1d2560`, barras `#adc6e5` solidas, sem degrade
- CSS todo escopado em `.sb-infographic` (nomes genericos: `.hero`, `.legend`, `.charts`...); variaveis `--fs-*`; titulo/subtitulo em Arial, cards/botao/avaliacao em DM Sans (ajustados pela imagem de referencia do usuario)
- Icone do card 1: `static/img/icon-brasil-fact-sheet.svg`; cards 2 e 3 com SVG inline
- Mobile <= 600px: graficos em 1 coluna e avaliacao empilhada (texto, gauge, legenda)
- Animacoes: mesmo IntersectionObserver (`.fs-animate`/`.fs-visible`); nao animar elementos com `transform` estatico (licao do fix v25 abaixo)
- Numeros dos graficos e do gauge sao fixos no HTML: atualizar a mao quando o Radar 2026 tiver resultado

Historico das folhas A4 (v15 a v25, substituidas em v26) no `docs/design.md`. Licao que continua valendo:

**Fix v25 — legenda do gauge perdia centralizacao:** `.legend` centraliza via `left:50% + transform:translateX(-50%)`; a animation `fs-up` (v23) define `transform:translateY(...)` na keyframe, e como CSS nao mescla transforms, a animation substitui o transform inteiro — com `fill-mode:both` o valor final ficava permanente, perdendo o `-50%` em X (legenda com borda esquerda no centro do sheet, cortada a direita). Corrigido com nova keyframe `fs-up-centered` que reafirma `translateX(-50%)` em todo frame. **Cuidado ao adicionar `animation` com `transform` em qualquer elemento que ja se posicione via `transform` estatico (ex.: `translateX(-50%)` para centralizar) — a keyframe precisa incluir esse transform em todos os frames, senao ele se perde.**

**FAQ — textos atuais (v25):**
- "Qual o escopo do Radar Brasil?": 2 paragrafos (escopo federal + 3 fatores do recorte)
- "Quais os fatores predominantes?": 5 paragrafos incluindo Ponderacao por relevancia federativa

Linha de divisao: border-top 1px solid rgba(38,69,132,.10) no meto-scroll-section.

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
