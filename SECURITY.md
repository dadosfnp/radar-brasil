# Política de Segurança — Radar Brasil

## Reportar uma Vulnerabilidade

Se você encontrar uma vulnerabilidade de segurança neste projeto, **não abra uma issue pública**.

Entre em contato diretamente pelo e-mail: **[bruno.marra@fnp.org.br](mailto:bruno.marra@fnp.org.br)**

Inclua na mensagem:
- Descrição clara do problema
- Passos para reproduzir
- Impacto potencial
- Sugestão de correção (se tiver)

Responderemos em até **48 horas** e trabalharemos para corrigir o problema o mais rápido possível.

---

## Configurações de Segurança em Produção

O projeto aplica automaticamente os seguintes controles quando `ENV=production`:

| Configuração | Valor |
|---|---|
| `DEBUG` | `False` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SECURE_HSTS_SECONDS` | `31536000` (1 ano) |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` |
| `SECURE_HSTS_PRELOAD` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `SESSION_COOKIE_HTTPONLY` | `True` |
| `CSRF_COOKIE_HTTPONLY` | `True` |
| `X_FRAME_OPTIONS` | `DENY` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |
| `SECURE_REFERRER_POLICY` | `strict-origin-when-cross-origin` |

---

## Boas Práticas Adotadas

- **Secrets**: nunca commitados — lidos exclusivamente de variáveis de ambiente (`.env` está no `.gitignore`)
- **Banco de dados**: queries via ORM Django (sem SQL concatenado)
- **Dependências**: listadas no `requirements.txt`, atualizadas periodicamente
- **Validação de entrada**: parâmetros de API validados antes do uso (retornam 400 em caso inválido)
- **HTTPS**: redirecionamento forçado em produção via `SECURE_SSL_REDIRECT`

---

## Verificar localmente

```bash
# Checa configurações de segurança para deploy
python manage.py check --deploy
```

Os avisos exibidos em ambiente de desenvolvimento (`DEBUG=True`) são esperados e resolvidos automaticamente em produção.
