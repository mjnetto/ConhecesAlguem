# 🚂 Deploy Rápido na Railway

## ⚡ Passo a Passo Rápido

### 1. **Push para GitHub**
```bash
git add .
git commit -m "Preparado para deploy Railway"
git push origin main
```

### 2. **Criar Projeto na Railway**

1. Acesse [railway.app](https://railway.app)
2. Login com GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecione seu repositório

### 3. **Adicionar PostgreSQL**

1. No projeto → "New" → "Database" → "Add PostgreSQL"
2. A Railway cria automaticamente `DATABASE_URL`

### 4. **Configurar Variáveis (IMPORTANTE!)**

No painel do projeto → "Variables" → Adicione:

```bash
SECRET_KEY=o7*n-9$t-cyiw6i*q@=_eanv5os)#3*u6gb)z8ug*dslsgaw!s
DEBUG=False
ALLOWED_HOSTS=*.railway.app
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-app-password-gmail
DEFAULT_FROM_EMAIL=noreply@conhecesalguem.ao
BASE_URL=https://seu-projeto.railway.app
ADMIN_EMAIL=admin@conhecesalguem.ao
```

**⚠️ IMPORTANTE:** 
- Substitua `BASE_URL` pelo domínio real do Railway (será algo como `seu-projeto.railway.app`)
- Para Gmail, use uma "App Password", não a senha normal

### 5. **Deploy Automático**

A Railway detecta automaticamente:
- ✅ `Procfile` - comando de start
- ✅ `requirements.txt` - dependências
- ✅ `runtime.txt` - Python 3.12

### 6. **Pós-Deploy (Terminal Railway)**

Após o deploy, acesse o terminal Railway ou use Railway CLI:

```bash
# Criar superusuário
railway run python manage.py createsuperuser

# Carregar dados iniciais
railway run python manage.py loaddata fixtures/provinces.json
railway run python manage.py loaddata fixtures/luanda_cities.json
railway run python manage.py loaddata fixtures/luanda_neighborhoods.json
railway run python manage.py loaddata fixtures/service_categories.json
```

### 7. **Configurar Domínio (Opcional)**

1. Railway → Settings → Domains
2. Clique "Generate Domain" ou adicione domínio customizado
3. Atualize `BASE_URL` e `ALLOWED_HOSTS` nas variáveis

---

## ✅ Checklist

- [ ] Código no GitHub
- [ ] Projeto criado na Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy bem-sucedido
- [ ] Superusuário criado
- [ ] Fixtures carregadas
- [ ] Site funcionando

---

## 🔍 Verificar Logs

Se algo der errado:
1. Railway → Deployments
2. Clique no deploy mais recente
3. Veja os logs de build e runtime

---

## 💡 Dicas

- **Domínio:** Railway gera um domínio `.railway.app` automaticamente
- **Email:** Use Gmail App Password ou SendGrid (100 emails/dia grátis)
- **Database:** Railway cria automaticamente, só precisa adicionar
- **Static Files:** Whitenoise já está configurado

---

**Pronto! Seu projeto estará no ar em poucos minutos! 🚀**

