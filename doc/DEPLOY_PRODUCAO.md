# 🚀 Deploy em Produção - Railway

Guia rápido para fazer deploy do projeto no Railway.

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositório Git (GitHub, GitLab, ou Bitbucket)
3. Projeto commitado e pronto para deploy

## ⚡ Deploy Rápido (5 minutos)

### 1. Conectar ao Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login (GitHub recomendado)
3. Clique em **"New Project"**
4. Selecione **"Deploy from GitHub repo"** (ou seu provider Git)
5. Selecione o repositório do projeto

### 2. Adicionar Banco de Dados PostgreSQL

1. No projeto Railway, clique em **"+ New"**
2. Selecione **"Database"** → **"Add PostgreSQL"**
3. Railway criará automaticamente um PostgreSQL
4. Copie a `DATABASE_URL` das variáveis de ambiente (disponível automaticamente)

### 3. Configurar Variáveis de Ambiente

No Railway, vá em **Variables** e adicione:

```env
# CRÍTICO - Gerar uma nova SECRET_KEY
SECRET_KEY=sua-secret-key-super-segura-aqui-gerar-com-python-secrets

# Produção
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.up.railway.app,seu-dominio.com

# Email (configurar SMTP real para produção)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@conhecesalguem.ao

# Admin
ADMIN_EMAIL=admin@conhecesalguem.ao

# Frontend
BASE_URL=https://seu-projeto.railway.app

# Phone Verification
WHATSAPP_VERIFICATION_ENABLED=True

# Currency
DEFAULT_CURRENCY=AOA
```

**⚠️ IMPORTANTE**: 
- A `DATABASE_URL` é **adicionada automaticamente** pelo Railway quando você adiciona o PostgreSQL
- **NUNCA** commite a `SECRET_KEY` no código!
- Gere uma nova `SECRET_KEY` para produção:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

### 4. Deploy Automático

1. Railway detecta automaticamente que é um projeto Django/Python
2. Executa comandos do `railway.json`:
   - **Migrações**: `python manage.py migrate --noinput`
   - **Static Files**: `python manage.py collectstatic --noinput`
   - **Servidor**: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

3. O deploy acontece automaticamente a cada push no branch principal

### 5. Criar Superusuário (Admin)

Após o primeiro deploy bem-sucedido:

1. No Railway, vá em **Deployments** → clique nos **"..."** do deployment
2. Selecione **"View Logs"**
3. Clique na aba **"Shell"** (ou use Railway CLI)
4. Execute:
   ```bash
   python manage.py createsuperuser
   ```
5. Siga as instruções para criar o admin

### 6. Carregar Dados Iniciais

No mesmo shell do Railway:

```bash
python manage.py loaddata fixtures/provinces.json
python manage.py loaddata fixtures/luanda_cities.json
python manage.py loaddata fixtures/luanda_neighborhoods.json
python manage.py loaddata fixtures/service_categories.json
```

### 7. Configurar Domínio Customizado (Opcional)

1. No Railway, vá em **Settings** → **Domains**
2. Clique em **"Generate Domain"** para obter um domínio Railway
3. Ou adicione seu domínio customizado (ex: `conhecesalguem.ao`)

## ✅ Verificação Pós-Deploy

- [ ] Site acessível em `https://seu-projeto.railway.app`
- [ ] Admin funcionando: `https://seu-projeto.railway.app/admin`
- [ ] Página inicial carrega corretamente
- [ ] Banco de dados conectado (verificar logs)
- [ ] Arquivos estáticos carregando (CSS, imagens)
- [ ] Superusuário criado
- [ ] Dados iniciais carregados (províncias, categorias)

## 🔧 Troubleshooting

### Erro: "No static files found"
- Verifique que `whitenoise` está no `requirements.txt`
- Verifique que `STATICFILES_STORAGE` está configurado no `settings.py`
- Execute manualmente: `python manage.py collectstatic`

### Erro: "Database connection failed"
- Verifique que o PostgreSQL está rodando no Railway
- Verifique que `DATABASE_URL` está nas variáveis de ambiente
- Verifique os logs do Railway

### Erro: "DEBUG is True in production"
- Garanta que `DEBUG=False` nas variáveis de ambiente do Railway
- Reinicie o serviço após alterar variáveis

### Erro: "ALLOWED_HOSTS"
- Adicione o domínio Railway às variáveis: `ALLOWED_HOSTS=*.railway.app`

## 📊 Monitoramento

- **Logs**: Railway mostra logs em tempo real
- **Metrics**: Railway mostra CPU, memória, etc.
- **Health Check**: Configure em `railway.json`

## 🔄 Atualizações Futuras

Qualquer push no branch principal faz deploy automático. Para fazer deploy manual:

1. Railway CLI:
   ```bash
   railway up
   ```

2. Ou via interface web: **Deployments** → **"Redeploy"**

---

**Próximos Passos**:
- [ ] Configurar email SMTP real (Gmail, SendGrid, etc)
- [ ] Configurar domínio customizado
- [ ] Configurar backup automático do banco
- [ ] Configurar monitoramento (Sentry, etc)


