# 📌 Pull Request – Radar Brasil

## ✅ Descrição do que foi feito

Explique de forma clara e objetiva o que foi desenvolvido neste Pull Request.

Exemplos:
- Ajustado layout do cabeçalho (`base_templates/base.html` + `base_statics/css/base.css`);
- Criada landing page pública (`setup/templates/municipios/landing.html`);
- Atualizado estilo dos cards da home (`setup/templates/municipios/inicio.html` + `base_statics/css/landing.css`);
- Corrigido bug de rota na app `municipios` (views / urls);

---

## 🧩 Tipo de alteração

- [ ] feat — Nova funcionalidade
- [ ] fix — Correção de bug
- [ ] refactor — Refatoração sem alterar comportamento
- [ ] style — Ajuste visual / CSS / HTML
- [ ] docs — Documentação
- [ ] chore — Configuração / dependências / scripts
- [ ] perf — Melhoria de performance

---

## 🗂 Áreas / Módulos afetados

Marque o(s) itens impactado(s) neste PR:

**Frontend (templates / estáticos)**  
- [ ] `base_templates`
- [ ] `setup/templates/municipios`
- [ ] `base_statics/css`
- [ ] `base_statics/js`
- [ ] `base_statics/img`

**Backend (Django / apps)**  
- [ ] `apps/municipios`
- [ ] `apps/indicadores`
- [ ] `apps/ranking`
- [ ] `apps/relatorios`
- [ ] `apps/usuarios`
- [ ] `apps/api`
- [ ] `setup` (configs do projeto / urls / settings)
- [ ] Outro: ______________________

---

## 🧪 Como testar

Descreva passo a passo como validar o PR no ambiente de desenvolvimento.

Exemplo:

1. Subir o servidor local:
   - `python manage.py runserver`
2. Acessar a página: `http://localhost:8000/municipios/landing/`
3. Verificar se:
   - [ ] O cabeçalho renderiza corretamente em diferentes resoluções;
   - [ ] O botão **“Acessar painéis”** leva para `/municipios/home/`;
   - [ ] Os links de redes sociais (rodapé) abrem as URLs corretas;
4. Repetir o teste em:
   - [ ] Chrome
   - [ ] Firefox
   - [ ] Outro: ____________

Adapte os passos acima para o que este PR realmente altera.

---

## 📸 Evidências visuais (se aplicável)

Cole prints, GIFs ou vídeos que comprovem o funcionamento da alteração.

---

## ⚠️ Impactos e riscos

Este PR:

- [ ] Não afeta produção diretamente (apenas desenvolvimento / `next`)
- [ ] Afeta apenas camada visual (HTML / CSS)
- [ ] Afeta rotas ou navegação (URLs, menus, links)
- [ ] Afeta lógica de negócio (views, serializers, modelos)
- [ ] Afeta dados, filtros ou cálculos (indicadores, ranking, relatórios)

---

## 🔁 Testes realizados

Marque tudo o que foi efetivamente testado:

- [ ] Testado localmente (`runserver`)
- [ ] Testado em ambiente de desenvolvimento / `next`
- [ ] Testes de navegação entre páginas (landing → início → detalhes)
- [ ] Testes de responsividade (desktop / tablet / mobile)
- [ ] Testes de links externos (redes sociais, C40, GCoM, FNP)
- [ ] Testes dos endpoints de API (se aplicável)
- [ ] Testes unitários / automatizados:
  - Comando: `_________________________`

---

## ✅ Checklist final do autor

- [ ] Revisei o código modificado (`git diff`)
- [ ] Nenhum arquivo sensível foi incluído (`.env`, senhas, chaves)
- [ ] Não inclui arquivos desnecessários (`__pycache__`, `.venv`, etc.)
- [ ] Sem conflitos conhecidos com a branch de destino
- [ ] Descrição do PR clara e objetiva
- [ ] Checklist de testes preenchido

---

## 🔗 Branches

Preencha com o nome correto das branches usadas:

- **Origem (desenvolvimento):** `brunofnp/radar-brasil-next:feature/nome-da-feature`
- **Destino (merge):**  
  - Ambiente de desenvolvimento: `brunofnp/radar-brasil-next:main`  
  - Posterior promoção para produção: `brunofnp/radar-brasil-main:main`