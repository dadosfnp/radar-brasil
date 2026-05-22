# Guia de Contribuição — Radar Brasil

## Fluxo de trabalho Git

```
feature/nome-da-feature  →  next  →  main (produção)
bugfix/nome-do-bug       ↗
```

**Regras obrigatórias:**
- Nunca commitar diretamente em `next` ou `main`
- Sempre criar uma branch `feature/` ou `bugfix/` a partir de `next`
- Fazer merge em `next` antes de subir para `main`
- `main` é a branch de produção (Render) — só recebe via merge de `next`

---

## Passo a passo

```bash
# 1. Atualizar next local
git checkout next
git pull origin next

# 2. Criar branch de trabalho
git checkout -b feature/nome-da-feature

# 3. Desenvolver e commitar
git add arquivo.py
git commit -m "feat: descrição clara do que foi feito"

# 4. Merge em next
git checkout next
git merge --no-ff feature/nome-da-feature -m "merge feature/nome-da-feature: resumo"
git branch -d feature/nome-da-feature

# 5. Subir para os dois remotes
git push origin next
git push prod next:main
```

---

## Mensagens de commit

Seguimos o padrão **Conventional Commits**:

```
<tipo>: <descrição curta em português>
```

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `style` | Ajuste visual (CSS/HTML sem mudança de comportamento) |
| `refactor` | Refatoração sem alterar comportamento |
| `docs` | Documentação |
| `test` | Adição ou correção de testes |
| `chore` | Configuração, dependências, build |
| `perf` | Melhoria de performance |
| `merge` | Merge de branches |

**Exemplos:**
```
feat: adiciona filtro por região no mapa georreferenciado
fix: corrige posicionamento dos labels de países no mapa Nota País
style: ajusta largura das abas no mobile
docs: atualiza CHANGELOG com alterações da sessão
```

---

## Padrões de código

### Python

- Formatação: `black --line-length 100`
- Lint: `flake8` (config em `.flake8`)
- Testes: `pytest` (config em `pytest.ini`)

```bash
# Verificar antes de commitar
black apps setup --check
flake8 apps setup
pytest apps/indicadores/tests.py -v
```

### CSS

- Cada página tem seu próprio arquivo em `static/css/`
- Prefixo de classe por página: `.np-` (Nota País), `.mg-` (Mapa Georreferenciado), `.pm-` (Painel Multinível), etc.
- Usar variáveis CSS definidas em `base.css` (`--color-primary`, `--radius-lg`, `--shadow-md`, etc.)
- Evitar cores hardcoded — preferir as variáveis do `:root`

### JavaScript

- Cada página tem seu próprio arquivo em `static/js/`
- Sem dependências de build — JS vanilla direto no browser
- Constantes e dados em `const` no topo do arquivo

---

## Estrutura do projeto

```
apps/
  indicadores/   ← views, services, API, testes
  municipios/    ← views, urls das páginas principais
  api/           ← app DRF (não usado ativamente)
  usuarios/      ← gestão de usuários
static/
  css/           ← um arquivo por página
  js/            ← um arquivo por página
templates/
  municipios/    ← templates das páginas
base_templates/  ← base.html, header, footer
setup/           ← settings, urls raiz, wsgi
docs/            ← CHANGELOG, documentação por página
```

---

## Documentação

Após cada conjunto de alterações:

1. Atualizar `docs/CHANGELOG.md` com o que foi feito
2. Se criou/modificou uma página: atualizar ou criar `docs/<nome-da-pagina>.md`

---

## Ambiente de desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar servidor
python manage.py runserver

# Rodar testes
pytest

# Verificar segurança
python manage.py check --deploy
```

Copie `.env.example` para `.env` e preencha os valores antes de rodar.
