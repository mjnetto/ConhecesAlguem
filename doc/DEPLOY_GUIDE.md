# 🚀 Guia de Deploy - Conheces Alguém?

## 📋 Checklist Pré-Deploy

### ✅ Funcionalidades Testadas
- [x] Fluxo de booking completo
- [x] Registro de profissionais
- [x] Login de clientes e profissionais
- [x] Sistema de reviews
- [x] Emails funcionando
- [x] Upload de imagens
- [x] Validações de formulários

---

## 🌐 Plataformas Recomendadas

### **Railway** (Recomendado - Fácil e Gratuito)
- [x] Suporta PostgreSQL
- [x] Deploy automático via Git
- [x] Variáveis de ambiente simples
- [x] SSL automático

### **Render**
- [x] Free tier disponível
- [x] PostgreSQL incluído
- [x] Deploy via Git

### **Heroku**
- [x] Popular e confiável
- [x] PostgreSQL addon
- [x] Deploy simples

---

## 📝 Passos para Deploy

### 1. **Preparar o Projeto**

```bash
# Garantir que todas as migrações estão criadas
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser
```

### 2. **Configurar Variáveis de Ambiente**

Criar arquivo `.env` na plataforma de deploy:

```bash
# Django
SECRET_KEY=suachave-secreta-muito-longa-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Database (geralmente fornecido pela plataforma)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-de-app  # Use App Password no Gmail
DEFAULT_FROM_EMAIL=noreply@conhecesalguem.ao
BASE_URL=https://seu-dominio.com
ADMIN_EMAIL=admin@conhecesalguem.ao

# Storage (para produção, use AWS S3 ou similar)
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=
```

### 3. **Arquivos Necessários para Deploy**

#### **Procfile** (para Railway/Heroku):
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application
```

#### **runtime.txt** (opcional, especificar Python):
```
python-3.12.0
```

### 4. **Configurações Adicionais**

#### **Whitenoise para Arquivos Estáticos** (já no requirements.txt)
O projeto já tem `whitenoise` configurado para servir arquivos estáticos em produção.

#### **Media Files em Produção**
Recomenda-se usar AWS S3 ou similar. O projeto já tem `django-storages` no requirements.txt.

---

## 🔒 Segurança

### Checklist de Segurança:

- [x] `DEBUG=False` em produção
- [x] `SECRET_KEY` única e segura
- [x] `ALLOWED_HOSTS` configurado
- [x] SSL/HTTPS ativado
- [x] Senhas de admin fortes
- [x] Emails configurados

---

## 📧 Configurar Email

### Para Gmail:
1. Ativar verificação em 2 etapas
2. Gerar "App Password"
3. Usar o App Password no `EMAIL_HOST_PASSWORD`

### Para outros serviços:
- **SendGrid**: Oferece 100 emails/dia grátis
- **Mailgun**: Boa opção para produção
- **AWS SES**: Se já usar AWS

---

## 🗄️ Database

### PostgreSQL em Produção:
- Use o PostgreSQL fornecido pela plataforma (Railway, Render)
- Ou configure AWS RDS, DigitalOcean, etc.
- Certifique-se de fazer backup regular

### Migrações:
```bash
python manage.py migrate
```

---

## 📁 Arquivos Estáticos e Media

### Opção 1: Whitenoise (simples)
- Já configurado
- Serve arquivos estáticos
- Para media files pequenos também funciona

### Opção 2: AWS S3 (recomendado para produção)
- Configure `django-storages`
- Use S3 para media files
- Melhor performance

---

## ✅ Pós-Deploy

### 1. **Criar Superusuário**
```bash
python manage.py createsuperuser
```

### 2. **Carregar Dados Iniciais**
```bash
python manage.py loaddata fixtures/provinces.json
python manage.py loaddata fixtures/luanda_cities.json
python manage.py loaddata fixtures/luanda_neighborhoods.json
python manage.py loaddata fixtures/service_categories.json
```

### 3. **Testar Funcionalidades**
- [ ] Homepage carrega
- [ ] Busca funciona
- [ ] Booking flow completo
- [ ] Registro de profissional
- [ ] Login funciona
- [ ] Emails são enviados
- [ ] Admin funciona

---

## 🔍 Monitoramento

### Logs:
- Verifique logs da plataforma regularmente
- Configure alertas de erro

### Performance:
- Monitore tempo de resposta
- Verifique uso de recursos

---

## 📞 Suporte

Em caso de problemas:
1. Verifique logs da aplicação
2. Verifique variáveis de ambiente
3. Teste localmente primeiro
4. Verifique configurações de email/database

---

**Boa sorte com o deploy! 🚀**

