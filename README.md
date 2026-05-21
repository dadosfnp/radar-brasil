#  Radar Brasil — Federalismo Climático
Inteligência Climática e Interfederativa para Municípios Brasileiros.

O **Radar Brasil** é uma plataforma desenvolvida em Django para análise, processamento e visualização de dados sobre ações climáticas no território nacional. O sistema integra planilhas, APIs geográficas e dados públicos em painéis interativos, permitindo avaliar a cooperação interfederativa nas políticas climáticas e identificar o posicionamento de cada município no contexto nacional e global.

---

##  Destaques do Sistema

-  **Mapa Georreferenciado:** Visualização geográfica interativa (Leaflet.js) dos municípios com financiamento climático, com filtros por região, estado, porte, eixo e modalidade de financiamento.
-  **Nota País:** Mapa-múndi com a coalizão CHAMP de signatários, scores por país e filtros por continente — com exportação via html2canvas.
-  **Painel Multinível:** Avaliação dos municípios em quatro eixos (Governança, Políticas e Planos, Programas, Linha de Financiamento), com dados lidos dinamicamente do Google Sheets.
-  **Financiamento Climático:** Painel de análise dos fluxos de financiamento climático no Brasil com gráficos e indicadores agregados.
-  **Avaliação e Ranking:** Ferramentas de avaliação comparativa e ranking entre municípios.
-  **Linha do Tempo:** Histórico visual das ações e marcos do Federalismo Climático no Brasil.
-  **Data Engine:** Leitura automatizada do Google Sheets com cache de 30 minutos, suporte a planilhas `.xlsx`/`.xls` e pipeline de importação via management commands.
-  **Design Glassmorphism:** Interface com backdrop-filter, cards translúcidos, tipografia Sora + DM Sans + DM Mono e background `#bdd6e0`.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 6.0.1 · Python 3.10+ |
| API | Django REST Framework |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL via Render |
| Dados | pandas · openpyxl · xlrd · gspread (Google Sheets) |
| Mapas | Leaflet.js · html2canvas |
| Estáticos | WhiteNoise |
| Variáveis de ambiente | python-dotenv |

---

##  Como Começar

### Pré-requisitos

- Python 3.10+
- Ambiente virtual (`venv`)
- Credenciais de acesso ao Google Sheets (arquivo `credentials.json`)

### Instalação Rápida

**Clone o projeto e entre na pasta:**
```bash
git clone <url-do-repo>
cd radar-brasil
```

**Configure o ambiente:**
```bash
python -m venv venv
./venv/Scripts/activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

**Configure as variáveis de ambiente** — crie um arquivo `.env` na raiz:
```env
SECRET_KEY=sua-chave-secreta
DEBUG=True
```

**Prepare o banco e os estáticos:**
```bash
python manage.py migrate
python manage.py collectstatic
```

**Inicie o servidor:**
```bash
python manage.py runserver
```

---

## 📈 Comandos de Dados

| Comando | Descrição |
|---|---|
| `popular_coords_municipios` | Popula as coordenadas geográficas dos municípios a partir do `municipios_coords.json` |

Os dados dinâmicos (Painel Multinível, Financiamento Climático, Avaliação) são lidos diretamente do Google Sheets via `gspread` com cache em memória de 30 minutos. As credenciais devem ser configuradas conforme a documentação do Google Cloud.

---

##  Estrutura do Projeto

```text
radar-brasil/
├── apps/
│   ├── municipios/          Rotas, views e modelos principais
│   ├── indicadores/
│   │   ├── views.py         Views Django (render + JsonResponse)
│   │   ├── urls.py          Rotas das APIs e páginas
│   │   └── services/
│   │       ├── financiamento_climatico.py
│   │       ├── painel_multinivel.py
│   │       ├── avaliacao_painel.py
│   │       └── mapa_georreferenciado.py
│   ├── ranking/             Rankings comparativos entre municípios
│   ├── relatorios/          Geração de relatórios
│   ├── usuarios/            Autenticação e perfis
│   └── api/                 Endpoints REST
├── templates/municipios/    Um template HTML por página
├── static/
│   ├── css/                 Um CSS por página
│   ├── js/                  Um JS por página
│   └── img/                 Imagens e ícones
├── base_templates/          Layout base (base.html, header, footer)
├── docs/                    Documentação técnica e CHANGELOG
└── setup/                   Configurações Django (settings, urls, wsgi)
```

---

##  Desenvolvimento e Contribuição

Para manter a integridade e uniformidade do projeto, seguimos padrões rigorosos de desenvolvimento.

- **Commits:** Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) (`feat:`, `fix:`, `style:`, `docs:`, `refactor:`).
- **Branching:** Nunca trabalhe diretamente na branch `next`. Use `feat/` ou `fix/` para novas funcionalidades e correções.
- **Pull Requests:** Use o template em `.github/PULL_REQUEST_TEMPLATE.md` — ele é preenchido automaticamente pelo GitHub.
- **Documentação:** Toda alteração relevante deve ser registrada em [`docs/CHANGELOG.md`](docs/CHANGELOG.md).
- **Padrão de arquivo:** cada página tem seu próprio template, CSS e JS. Não misture estilos ou scripts entre páginas.

---

##  Documentação Técnica

A pasta [`docs/`](docs/) contém a documentação técnica detalhada de cada módulo:

| Documento | Conteúdo |
|---|---|
| [CHANGELOG.md](docs/CHANGELOG.md) | Histórico completo de todas as alterações |
| [mapa-georreferenciado.md](docs/mapa-georreferenciado.md) | Filtros, JS e estrutura do Mapa Georreferenciado |
| [financiamento-climatico.md](docs/financiamento-climatico.md) | Painel de Financiamento Climático |
| [nota-pais.md](docs/nota-pais.md) | Mapa-múndi Nota País e coalizão CHAMP |

---

 **Desenvolvido por:** FNP — Frente Nacional de Prefeitos | 📄 **Licença:** Uso Interno / Restrito
