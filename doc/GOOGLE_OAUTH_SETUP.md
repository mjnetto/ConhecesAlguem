# Configuração do Login com Google (OAuth2)

Este guia explica como configurar o login com Google OAuth2 na plataforma Conheces Alguém?.

## 📋 Pré-requisitos

1. Conta Google (Gmail)
2. Acesso ao [Google Cloud Console](https://console.cloud.google.com/)

## 🔧 Passo a Passo

### 1. Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Clique em "Selecionar um projeto" → "Novo projeto"
3. Nome do projeto: `Conheces Alguém`
4. Clique em "Criar"

### 2. Ativar Google+ API

1. No menu lateral, vá em **APIs e Serviços** → **Biblioteca**
2. Procure por "Google+ API" ou "Google Identity"
3. Clique em "Ativar"

### 3. Criar Credenciais OAuth

1. Vá em **APIs e Serviços** → **Credenciais**
2. Clique em **+ Criar credenciais** → **ID do cliente OAuth**
3. Configure:
   - **Tipo de aplicativo**: Aplicativo da Web
   - **Nome**: Conheces Alguém - Web App
   - **Origens JavaScript autorizadas**:
     - `http://localhost:8000` (desenvolvimento)
     - `https://conhecesalguem-production.up.railway.app` (produção - substitua pelo seu domínio)
     - Ou o domínio que o Railway forneceu para sua aplicação
   - **URIs de redirecionamento autorizados**:
     - `http://localhost:8000/accounts/google/login/callback/` (desenvolvimento)
     - `https://conhecesalguem-production.up.railway.app/accounts/google/login/callback/` (produção - substitua pelo seu domínio)
4. Clique em **Criar**

### 4. Copiar Credenciais

Após criar, você verá:
- **ID do Cliente** (Client ID): `xxxxxxxxxxxx-xxxxxxxxxxxx.apps.googleusercontent.com`
- **Segredo do Cliente** (Client Secret): `xxxxxxxxxxxx`

⚠️ **IMPORTANTE**: Guarde o Secret com segurança!

### 5. Configurar no Projeto

#### Desenvolvimento (local)

No arquivo `.env`:
```bash
GOOGLE_OAUTH_CLIENT_ID=seu-client-id-aqui
GOOGLE_OAUTH_CLIENT_SECRET=seu-client-secret-aqui
```

#### Produção (Railway)

1. No Railway, vá em **Variables**
2. Adicione as variáveis:
   - `GOOGLE_OAUTH_CLIENT_ID` = seu-client-id
   - `GOOGLE_OAUTH_CLIENT_SECRET` = seu-client-secret

### 6. Executar Migrações

```bash
python manage.py migrate
```

### 7. Criar Site no Django Admin

O django-allauth precisa de um Site configurado:

1. Acesse `/admin/sites/site/`
2. Edite o site padrão (id=1):
   - **Nome do domínio**: `conhecesalguem-production.up.railway.app` (ou seu domínio Railway, ou `localhost:8000` em dev)
   - **Nome de exibição**: `Conheces Alguém?`
3. Salve

Ou via shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'conhecesalguem-production.up.railway.app'  # Substitua pelo seu domínio
site.name = 'Conheces Alguém?'
site.save()
```

**💡 Para descobrir seu domínio no Railway:**
- Railway Dashboard → Seu Serviço Web → Settings → Domains
- Ou verifique a variável `RAILWAY_PUBLIC_DOMAIN` nas Variables
- O domínio padrão geralmente é algo como: `seu-projeto-production.up.railway.app`

## 🎯 Como Funciona

1. Usuário clica em "Entrar com Google"
2. É redirecionado para Google para autorizar
3. Google retorna com email e nome
4. Sistema verifica se já existe conta vinculada:
   - **Sim**: Faz login automaticamente
   - **Não**: Pergunta se é Cliente ou Profissional
5. Cria/atualiza conta com informações do Google

## ✅ Testando

1. Acesse `/accounts/cliente/login/`
2. Clique em "Entrar com Google"
3. Escolha sua conta Google
4. Autorize o acesso
5. Escolha "Cliente" ou "Profissional"
6. Deve fazer login com sucesso!

## 🔒 Segurança

- ✅ Credenciais armazenadas em variáveis de ambiente
- ✅ HTTPS obrigatório em produção
- ✅ CSRF protection ativo
- ✅ OAuth2 PKCE habilitado

## 🐛 Troubleshooting

### Erro: "redirect_uri_mismatch"
- Verifique se as URIs de redirecionamento estão corretas no Google Console
- Deve ser exatamente: `/accounts/google/login/callback/`

### Erro: "invalid_client"
- Verifique se as credenciais estão corretas no `.env` ou Railway
- Nome das variáveis devem ser exatas: `GOOGLE_OAUTH_CLIENT_ID` e `GOOGLE_OAUTH_CLIENT_SECRET`

### Login funciona mas não cria Client/Professional
- Verifique se o adapter customizado está no settings: `SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'`

## 📚 Recursos

- [Documentação django-allauth](https://django-allauth.readthedocs.io/)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)

