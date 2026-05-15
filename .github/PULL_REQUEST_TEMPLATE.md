# Pull Request — Radar Brasil

## Descrição do que foi feito

Explique de forma clara e objetiva o que foi desenvolvido neste Pull Request.

Exemplos:
- Ajustado layout do cabeçalho (`base_templates/base.html` + `static/css/base.css`)
- Criada nova página de indicador (`templates/municipios/nome.html` + `static/css/nome.css`)
- Corrigido bug de filtro na view `indicadores` (`apps/indicadores/views.py`)
- Atualizado estilo dos cards da home (`templates/municipios/inicio.html` + `static/css/inicio.css`)

---

## Tipo de alteração

- [ ] `feat` — Nova funcionalidade
- [ ] `fix` — Correção de bug
- [ ] `refactor` — Refatoração sem alterar comportamento
- [ ] `style` — Ajuste visual / CSS / HTML
- [ ] `docs` — Documentação
- [ ] `chore` — Configuração / dependências / scripts
- [ ] `perf` — Melhoria de performance

---

## Áreas e arquivos afetados

**Frontend (templates / estáticos)**
- [ ] `base_templates/` — base.html, header, footer
- [ ] `templates/municipios/` — páginas individuais
- [ ] `static/css/` — estilos por página
- [ ] `static/js/` — lógica por página
- [ ] `static/img/` — imagens e ícones

**Backend (Django)**
- [ ] `apps/municipios/` — views, urls, models
- [ ] `apps/indicadores/` — views, urls, services, APIs
- [ ] `apps/ranking/`
- [ ] `apps/relatorios/`
- [ ] `apps/usuarios/`
- [ ] `apps/api/`
- [ ] `setup/` — settings, urls raiz, wsgi

**Documentação**
- [ ] `docs/CHANGELOG.md` atualizado com as alterações deste PR
- [ ] Documentação técnica da página criada/alterada atualizada em `docs/`

---

## Como testar

Descreva passo a passo como validar o PR no ambiente de desenvolvimento.

1. Clonar a branch e subir o servidor:
   ```bash
   git checkout <nome-da-branch>
   python manage.py runserver
   ```
2. Acessar a URL afetada: `http://localhost:8000/...`
3. Verificar se:
   - [ ] A página renderiza sem erros no console
   - [ ] Os filtros / interações funcionam corretamente
   - [ ] O layout está correto em desktop e mobile
4. Testar nos navegadores:
   - [ ] Chrome
   - [ ] Firefox
   - [ ] Outro: ___________

---

## Evidências visuais (se aplicável)

Cole prints, GIFs ou vídeos que comprovem o funcionamento da alteração.

> Dica: arraste a imagem diretamente aqui no GitHub para fazer o upload.

---

## Impactos e riscos

Este PR:

- [ ] Não afeta produção diretamente (apenas desenvolvimento / `next`)
- [ ] Afeta apenas camada visual (HTML / CSS)
- [ ] Afeta rotas ou navegação (URLs, menus, links)
- [ ] Afeta lógica de negócio (views, services, models)
- [ ] Afeta dados, filtros ou cálculos (indicadores, mapa, ranking)
- [ ] Requer migração de banco de dados (`python manage.py migrate`)
- [ ] Requer atualização de variáveis de ambiente (`.env`)

---

## Testes realizados

- [ ] Testado localmente (`runserver`)
- [ ] Sem erros no console do navegador
- [ ] Sem erros no terminal Django (500, 404, exceptions)
- [ ] Testes de responsividade (desktop / tablet / mobile)
- [ ] Testes de navegação entre páginas
- [ ] Testes dos filtros e interações da página
- [ ] Testes dos endpoints de API afetados (se aplicável)

---

## Checklist final do autor

- [ ] Revisei todo o código modificado (`git diff`)
- [ ] Nenhum arquivo sensível foi incluído (`.env`, `.secrets/`, senhas, chaves)
- [ ] Não inclui arquivos desnecessários (`__pycache__`, `.venv`, `venv`, `db.sqlite3`)
- [ ] Sem conflitos conhecidos com a branch `next`
- [ ] `docs/CHANGELOG.md` atualizado com as alterações deste PR
- [ ] Descrição do PR clara e objetiva
- [ ] Checklist de testes preenchido

---

## Branches

- **Branch de origem:** `feature/nome-da-feature` _(ou `fix/`, `style/`, `docs/`)_
- **Branch de destino:** `next`
- **Repositório:** `brunofnp/radar-brasil`
