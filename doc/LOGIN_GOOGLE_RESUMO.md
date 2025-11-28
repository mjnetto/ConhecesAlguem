# Login com Google - Resumo da Implementação

## ✅ O Que Foi Implementado

### 1. Configuração Base
- ✅ `django-allauth` instalado e configurado
- ✅ Google OAuth provider configurado
- ✅ Adaptadores customizados para integrar com modelos Client/Professional

### 2. Modelos Atualizados
- ✅ `Client.email` agora é único e pode ser usado para login
- ✅ `Client.google_id` adicionado para vincular conta Google
- ✅ `Professional.email` e `Professional.google_id` também implementados
- ✅ Telefone ainda funciona (retrocompatibilidade)

### 3. Fluxo de Login
1. Usuário clica em "Entrar com Google"
2. Redirecionado para Google OAuth
3. Após autorizar, volta para `/accounts/google-callback/`
4. Sistema verifica se já existe conta vinculada:
   - **Sim**: Login automático
   - **Não**: Pergunta se é Cliente ou Profissional
5. Cria/vincula conta e faz login

### 4. Templates
- ✅ Botão "Entrar com Google" no login de Cliente
- ✅ Botão "Entrar com Google" no login de Profissional
- ✅ Página para escolher tipo de conta (`choose_user_type.html`)
- ✅ Integração com registro de profissional (pré-preenche email/nome do Google)

### 5. Segurança
- ✅ OAuth2 PKCE habilitado
- ✅ CSRF protection
- ✅ HTTPS obrigatório em produção

---

## 📝 Próximos Passos (Configuração Necessária)

### 1. Criar Credenciais no Google Cloud Console
Siga o guia completo em: `doc/GOOGLE_OAUTH_SETUP.md`

**Resumo rápido:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie projeto → Ative Google+ API
3. Crie credenciais OAuth (ID do Cliente e Segredo)
4. Configure URIs de redirecionamento:
   - Dev: `http://localhost:8000/accounts/google/login/callback/`
   - Prod: `https://seu-dominio.railway.app/accounts/google/login/callback/`

### 2. Configurar Variáveis de Ambiente

**Desenvolvimento (.env):**
```bash
GOOGLE_OAUTH_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=seu-client-secret
```

**Produção (Railway):**
Adicione as mesmas variáveis no painel Railway → Variables

### 3. Executar Migrações
```bash
python manage.py migrate
```

### 4. Configurar Site no Django Admin
```python
# Via shell ou admin
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'seu-dominio.railway.app'  # ou localhost:8000 em dev
site.name = 'Conheces Alguém?'
site.save()
```

---

## 🎯 Benefícios

- ✅ **Gratuito** - Sem custos de SMS
- ✅ **Mais Seguro** - OAuth2 é padrão da indústria
- ✅ **Melhor UX** - Login rápido com um clique
- ✅ **Confiança** - Usuários confiam no Google
- ✅ **Retrocompatível** - Telefone ainda funciona

---

## 🔄 Compatibilidade

O sistema suporta **ambos os métodos**:
- **Login com Google** (novo, recomendado)
- **Login com Telefone** (antigo, ainda funciona)

Usuários podem escolher o método preferido!

---

## 📚 Documentação Completa

Veja `doc/GOOGLE_OAUTH_SETUP.md` para instruções detalhadas de configuração.

