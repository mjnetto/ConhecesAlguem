# 🔐 Configuração Google OAuth - Passo a Passo Completo

## 📍 PASSO 1: Descobrir o Domínio da Aplicação no Railway

1. Acesse o [Railway Dashboard](https://railway.app/dashboard)
2. Clique no seu projeto
3. Clique no serviço Web (geralmente chamado de algo como "web" ou o nome do projeto)
4. Vá na aba **"Settings"**
5. Role até **"Domains"** ou **"Networking"**
6. **Copie o domínio** que aparece (ex: `conhecesalguem-production.up.railway.app`)

**OU** verifique na aba **"Variables"**:
- Procure por `RAILWAY_PUBLIC_DOMAIN`
- Se existir, esse é o seu domínio

**Anote este domínio!** Você vai precisar dele várias vezes.

---

## 📍 PASSO 2: Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Clique no menu de projetos (canto superior esquerdo)
3. Clique em **"Novo Projeto"**
4. Preencha:
   - **Nome do projeto**: `Conheces Alguém` (ou qualquer nome)
   - **Organização**: Deixe padrão (se tiver)
5. Clique em **"Criar"**
6. Aguarde alguns segundos e selecione o projeto recém-criado

---

## 📍 PASSO 3: Ativar Google Identity API

1. No menu lateral esquerdo, clique em **"APIs e Serviços"** → **"Biblioteca"**
2. Na barra de busca, digite: **"Google Identity"** ou **"OAuth2"**
3. Clique em **"Google Identity Services API"** ou **"OAuth2 API"**
4. Clique em **"ATIVAR"**
5. Aguarde a confirmação

**Alternativa**: Procure por **"People API"** e ative também (alguns provedores OAuth precisam)

---

## 📍 PASSO 4: Configurar Tela de Consentimento OAuth

1. No menu lateral, vá em **"APIs e Serviços"** → **"Tela de consentimento OAuth"**
2. Selecione **"Externo"** (para desenvolvimento) ou **"Interno"** (se tiver Google Workspace)
3. Clique em **"Criar"**
4. Preencha:
   - **Nome do aplicativo**: `Conheces Alguém`
   - **Email de suporte do usuário**: Seu email
   - **Logo** (opcional): Pode pular por enquanto
   - **Domínios autorizados**: Adicione `railway.app`
5. Role até **"Escopos"**:
   - Clique em **"Adicionar ou remover escopos"**
   - Selecione:
     - `userinfo.email`
     - `userinfo.profile`
     - `openid`
   - Clique em **"Atualizar"**
6. Preencha **"Informações de contato do desenvolvedor"**: Seu email
7. Clique em **"Salvar e continuar"**
8. Na próxima tela, clique em **"Voltar ao painel"** (não precisa configurar mais nada agora)

---

## 📍 PASSO 5: Criar Credenciais OAuth

1. No menu lateral, vá em **"APIs e Serviços"** → **"Credenciais"**
2. Clique em **"+ CRIAR CREDENCIAIS"** no topo
3. Selecione **"ID do cliente OAuth"**
4. Configure:

   **Tipo de aplicativo**: `Aplicativo da Web`
   
   **Nome**: `Conheces Alguém - Web App`
   
   **Origens JavaScript autorizadas** (adicione uma por vez):
   - `http://localhost:8000`
   - `https://SEU-DOMINIO-RAILWAY` (substitua pelo domínio do Passo 1, ex: `https://conhecesalguem-production.up.railway.app`)
   
   **URIs de redirecionamento autorizados** (adicione uma por vez):
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/` (opcional, mas recomendado para compatibilidade)
   - `https://SEU-DOMINIO-RAILWAY/accounts/google/login/callback/` (substitua pelo domínio do Passo 1)
   
   ⚠️ **IMPORTANTE**: Para produção, SEMPRE use `https://` (não `http://`)

5. Clique em **"CRIAR"**

---

## 📍 PASSO 6: Copiar Credenciais

Após criar, uma janela aparecerá com:

- **ID do Cliente** (Client ID): `xxxxxxxxxxxx-xxxxxxxxxxxx.apps.googleusercontent.com`
- **Segredo do Cliente** (Client Secret): `xxxxxxxxxxxx`

⚠️ **IMPORTANTE**: 
- **COPIE AMBOS** e guarde em local seguro
- O Secret só aparece UMA VEZ!
- Se perder o Secret, terá que criar novas credenciais

**Anote:**
- Client ID: `________________________`
- Client Secret: `________________________`

---

## 📍 PASSO 7: Adicionar Credenciais no Railway

1. No Railway Dashboard, vá no seu serviço Web
2. Clique na aba **"Variables"**
3. Clique em **"+ New Variable"** (ou **"Raw Editor"**)
4. Adicione as seguintes variáveis (uma por vez):

   **Variável 1:**
   - **Key**: `GOOGLE_OAUTH_CLIENT_ID`
   - **Value**: Cole o Client ID do Passo 6
   - Clique em **"Add"**

   **Variável 2:**
   - **Key**: `GOOGLE_OAUTH_CLIENT_SECRET`
   - **Value**: Cole o Client Secret do Passo 6
   - Clique em **"Add"**

5. **Salve** (se necessário)

---

## 📍 PASSO 8: Configurar Site no Django Admin

Você precisa atualizar o Site do Django para usar o domínio correto.

### Opção A: Via Django Admin (Recomendado)

1. Acesse seu site: `https://SEU-DOMINIO/admin/` (ou `http://localhost:8000/admin/` em dev)
2. Faça login com sua conta admin
3. No menu, clique em **"Sites"** (dentro de "Sites")
4. Clique no site padrão (geralmente `example.com`)
5. Edite:
   - **Nome do domínio**: 
     - **Produção**: `SEU-DOMINIO-RAILWAY` (ex: `conhecesalguem-production.up.railway.app`)
     - **Dev**: `localhost:8000`
   - **Nome de exibição**: `Conheces Alguém?`
6. Clique em **"Salvar"**

### Opção B: Via Django Shell

1. No Railway, abra o terminal do serviço Web
2. Execute:
```bash
python manage.py shell
```
3. Cole e execute:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'https://conhecesalguem-production.up.railway.app/'  # Substitua pelo seu domínio
site.name = 'Conheces Alguém?'
site.save()
print(f"Site atualizado: {site.domain}")
exit()
```

### Opção C: Via Railway CLI (Se tiver instalado)

```bash
railway run python manage.py shell
```
Depois execute o mesmo código Python da Opção B.

---

## 📍 PASSO 9: Testar o Login

1. Acesse: `https://SEU-DOMINIO/accounts/cliente/login/`
2. Você deve ver um botão **"Entrar com Google"** ou **"Login com Google"**
3. Clique nele
4. Você será redirecionado para o Google
5. Escolha sua conta Google
6. Autorize o acesso
7. Você será redirecionado de volta e deve ver uma tela para escolher:
   - **Cliente** ou **Profissional**
8. Escolha um e deve fazer login com sucesso!

---

## ✅ Checklist Final

Confirme que você fez:

- [ ] Descobriu o domínio no Railway
- [ ] Criou projeto no Google Cloud Console
- [ ] Ativou Google Identity API
- [ ] Configurou tela de consentimento OAuth
- [ ] Criou credenciais OAuth com URIs corretas
- [ ] Copiou Client ID e Client Secret
- [ ] Adicionou variáveis no Railway (`GOOGLE_OAUTH_CLIENT_ID` e `GOOGLE_OAUTH_CLIENT_SECRET`)
- [ ] Atualizou Site no Django Admin
- [ ] Testou o login e funcionou!

---

## 🐛 Problemas Comuns

### Erro: "redirect_uri_mismatch"

**Causa**: A URI de redirecionamento no Google Console não está exata.

**Solução**:
1. Vá no Google Cloud Console → Credenciais
2. Edite sua credencial OAuth
3. Verifique se a URI é EXATAMENTE: `https://SEU-DOMINIO/accounts/google/login/callback/`
   - Deve terminar com `/callback/` (com barra no final)
   - Deve usar `https://` (não `http://`) em produção
   - Não pode ter espaços extras

### Erro: "invalid_client"

**Causa**: Credenciais incorretas ou variáveis com nomes errados.

**Solução**:
1. Verifique no Railway Variables se os nomes são EXATOS:
   - `GOOGLE_OAUTH_CLIENT_ID` (maiúsculas, com underscores)
   - `GOOGLE_OAUTH_CLIENT_SECRET` (maiúsculas, com underscores)
2. Verifique se não há espaços extras nas credenciais
3. Recrie as credenciais no Google se necessário

### Login funciona mas não cria Client/Professional

**Causa**: Adapter customizado não configurado.

**Solução**:
1. Verifique no `core/settings.py` se existe:
   ```python
   SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
   ```
2. Se não existir, adicione (deve estar na linha ~280 do settings.py)

### Site não encontrado

**Causa**: Site do Django não configurado corretamente.

**Solução**:
1. Execute: `python manage.py migrate` (garante que tabela Sites existe)
2. Configure o Site via Admin ou shell (Passo 8)

---

## 📚 Mais Informações

- Guia completo: `doc/GOOGLE_OAUTH_SETUP.md`
- Documentação django-allauth: https://django-allauth.readthedocs.io/
- Google OAuth2 Docs: https://developers.google.com/identity/protocols/oauth2

---

## 💡 Dica Pro

Se você ainda não tem um domínio customizado, o Railway fornece um domínio `.railway.app` que funciona perfeitamente. Você pode adicionar um domínio customizado depois sem precisar alterar as configurações do Google OAuth (apenas adicione a nova URI nas credenciais).

