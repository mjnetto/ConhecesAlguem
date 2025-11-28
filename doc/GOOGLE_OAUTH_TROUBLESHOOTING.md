# 🐛 Troubleshooting Google OAuth - redirect_uri_mismatch

## Erro: redirect_uri_mismatch

Este erro ocorre quando a URI de redirecionamento enviada pelo seu aplicativo **não corresponde exatamente** à URI configurada no Google Cloud Console.

### Causas Comuns

1. **Protocolo diferente** (HTTP vs HTTPS)
   - Seu app envia: `http://...`
   - Google Console espera: `https://...`

2. **Domínio diferente**
   - Seu app envia: `conhecesalguem-production.up.railway.app`
   - Google Console espera: `exemplo.com` (outro domínio)

3. **Path diferente**
   - Seu app envia: `/accounts/google/login/callback/`
   - Google Console espera: `/oauth/callback` (outro path)

4. **Barra final faltando ou extra**
   - Seu app envia: `/accounts/google/login/callback` (sem barra)
   - Google Console espera: `/accounts/google/login/callback/` (com barra)

5. **Porta na URI**
   - Seu app envia: `https://dominio.com:8080/callback/`
   - Google Console espera: `https://dominio.com/callback/` (sem porta)

6. **Espaços ou caracteres extras**
   - Seu app envia: `https://dominio.com/callback/ ` (com espaço no final)
   - Google Console espera: `https://dominio.com/callback/` (sem espaço)

## 📋 Checklist de Verificação

### 1. Verificar URI no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Vá em **APIs e Serviços** → **Credenciais**
3. Clique no seu **Client ID OAuth**
4. Na seção **"URIs de redirecionamento autorizados"**, verifique:
   - ✅ Está usando `https://` (não `http://`) para produção?
   - ✅ O domínio está correto?
   - ✅ O path está correto: `/accounts/google/login/callback/`
   - ✅ Termina com `/callback/` (com barra final)?
   - ✅ Não há espaços extras?

**URIs corretas para este projeto:**
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
https://conhecesalguem-production.up.railway.app/accounts/google/login/callback/
```

### 2. Verificar Site do Django

O django-allauth usa o Site do Django para gerar URLs. Verifique:

1. Acesse `/admin/sites/site/`
2. Edite o site padrão (id=1)
3. Verifique:
   - **Nome do domínio**: Deve ser `conhecesalguem-production.up.railway.app` (sem `https://`)
   - **Nome de exibição**: `Conheces Alguém?`

**Ou execute via shell:**
```bash
python manage.py update_site --domain conhecesalguem-production.up.railway.app
```

### 3. Verificar Configurações do Django

No `core/settings.py`, certifique-se de que tem:

```python
# Forçar HTTPS em produção
if not DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
```

### 4. Verificar Headers HTTP

O Railway deve estar enviando o header `X-Forwarded-Proto: https`. O Django detecta isso automaticamente com `SECURE_PROXY_SSL_HEADER`.

### 5. Verificar Variáveis de Ambiente

No Railway, verifique se tem:
- `RAILWAY_PUBLIC_DOMAIN` definida
- `DEBUG=False` em produção
- `GOOGLE_OAUTH_CLIENT_ID` definida
- `GOOGLE_OAUTH_CLIENT_SECRET` definida

## 🔧 Soluções

### Solução 1: Corrigir URI no Google Console

Se o erro mostra que está enviando `http://` mas você configurou `https://`:

1. **No Google Console**, adicione AMBAS as URIs (temporariamente para teste):
   ```
   http://conhecesalguem-production.up.railway.app/accounts/google/login/callback/
   https://conhecesalguem-production.up.railway.app/accounts/google/login/callback/
   ```
2. Teste novamente
3. Se funcionar com `http://`, o problema é que o Django não está detectando HTTPS
4. Se funcionar com `https://`, remova a URI `http://` e mantenha apenas `https://`

### Solução 2: Forçar HTTPS no Django

Adicione ao `core/settings.py`:

```python
# Forçar HTTPS para URLs geradas pelo django-allauth
if not DEBUG:
    # Força django-allauth a usar HTTPS
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    
    # Detecta HTTPS através do proxy do Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Outras configurações de segurança
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### Solução 3: Atualizar Site do Django

Execute:

```bash
python manage.py update_site --domain conhecesalguem-production.up.railway.app
```

Isso atualiza o Site para usar o domínio correto, garantindo que o django-allauth gere URLs corretas.

### Solução 4: Verificar Logs para Ver URI Real

Adicione logs temporários para ver qual URI está sendo enviada:

```python
# Em accounts/adapters.py, adicione:
import logging
logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Log da URL de callback que será usada
        callback_url = request.build_absolute_uri('/accounts/google/login/callback/')
        logger.error(f"Callback URL sendo enviada: {callback_url}")
```

### Solução 5: Usar MIDDLEWARE para Forçar HTTPS

Certifique-se de que o Railway está enviando o header correto. Adicione um middleware de debug:

```python
# Em core/middleware.py
class DebugHttpsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Debug: ver headers
        if request.path.startswith('/accounts/google/'):
            print(f"X-Forwarded-Proto: {request.META.get('HTTP_X_FORWARDED_PROTO')}")
            print(f"HTTPS: {request.is_secure()}")
            print(f"Host: {request.get_host()}")
        return self.get_response(request)
```

## 🎯 Diagnóstico Rápido

### Erro mostra: `redirect_uri=http://conhecesalguem-production.up.railway.app/...`

**Problema**: Django está gerando URL com HTTP

**Solução**:
1. Verifique se `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'` está no settings
2. Verifique se `SECURE_PROXY_SSL_HEADER` está configurado
3. Atualize o Site do Django
4. Adicione URI com `http://` no Google Console temporariamente para testar

### Erro mostra: `redirect_uri=https://outro-dominio.com/...`

**Problema**: Site do Django está configurado com domínio errado

**Solução**:
1. Atualize o Site no Django Admin
2. Execute `python manage.py update_site --domain conhecesalguem-production.up.railway.app`

### Erro mostra: `redirect_uri=https://conhecesalguem-production.up.railway.app/accounts/google/callback` (sem barra final)

**Problema**: Path sem barra final

**Solução**:
1. No Google Console, adicione URI COM barra final: `/accounts/google/login/callback/`
2. Certifique-se de que o django-allauth está gerando com barra final (deveria estar)

## 📚 Referências

- [Documentação Google OAuth - Erros de Autorização](https://developers.google.com/identity/protocols/oauth2/web-server?hl=pt-br#authorization-errors-redirect-uri-mismatch)
- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Django SECURE_PROXY_SSL_HEADER](https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header)

## ⚡ Solução Rápida (Try This First)

Se nada funcionar, tente esta sequência:

1. **No Google Console**, adicione TODAS estas URIs (temporariamente):
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   https://conhecesalguem-production.up.railway.app/accounts/google/login/callback/
   http://conhecesalguem-production.up.railway.app/accounts/google/login/callback/
   ```

2. **No Django Admin**, atualize o Site:
   - Domínio: `conhecesalguem-production.up.railway.app`
   - Nome: `Conheces Alguém?`

3. **Aguarde 10-15 minutos** para o Google processar as mudanças

4. **Teste novamente**

5. Se funcionar, remova as URIs `http://` do Google Console e mantenha apenas `https://`

