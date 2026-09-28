# CONSTRAINTS: Radar Brasil

Barra mínima de qualidade do projeto. **Ainda não é verificada no CI**: por enquanto é um
contrato para revisão manual (humana ou de agente) antes de cada merge em `next`.
Baixar um limite exige registrar o motivo aqui, no mesmo commit.

## 1. Performance: peso de imagens

**Regra:** nenhuma imagem nova em `static/img/` acima de **500 KB**. Fotos em JPG/WebP,
largura máxima 1920px.

Situação em 2026-09-28 (acima do limite, a otimizar):

| Arquivo | Tamanho |
|---|---|
| `cidade-metodologia.jpg` | 8,7 MB |
| `natureza-metodologia.jpg` | 5,9 MB |
| `sociedade-metodologia.jpg` | 5,4 MB |
| `clima-metodologia.jpg` | 4,3 MB |
| `fundo-bg.png` | 930 KB |

Verificar: `Get-ChildItem static\img -File | Where-Object Length -gt 500KB`

## 2. Testes: services Python

**Regra:** toda mudança em `apps/indicadores/services/` ou nas views de API vem com teste
em `apps/indicadores/tests.py`. Testes existentes nunca são apagados ou pulados
(`skip`/`xfail`) para o CI passar.

Cobertura ainda não medida (`pytest-cov` está no `requirements-dev.txt`, mas não no CI).
Próximo passo: medir a linha de base com
`pytest apps/indicadores/tests.py --cov=apps/indicadores/services` e fixar o limite aqui
sem ficar abaixo dela.

## 3. Acessibilidade: básico

**Regra:**

- Toda `<img>` tem `alt` (vazio `alt=""` só para imagem decorativa).
- Touch targets com `min-height: 44px` em mobile (padrão já adotado).
- Texto com contraste WCAG AA (4.5:1) contra o fundo: atenção a texto branco translúcido
  sobre o navy e a texto sobre o glassmorphism.

## Fora do escopo (por ora)

Cobertura de JS e Lighthouse no CI: não há build de JS no projeto; reavaliar se isso mudar.
