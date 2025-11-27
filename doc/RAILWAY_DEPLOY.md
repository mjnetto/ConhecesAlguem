# 🚂 Deploy na Railway - Guia Completo

## 📋 Passo a Passo

### 1. **Criar Conta e Projeto na Railway**

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Conecte seu repositório

### 2. **Adicionar PostgreSQL Database**

1. No projeto Railway, clique em "New"
2. Selecione "Database" → "Add PostgreSQL"
3. A Railway criará automaticamente a variável `DATABASE_URL`

### 3. **Configurar Variáveis de Ambiente**

No painel do projeto Railway, vá em "Variables" e adicione:

```bash
# Django
SECRET_KEY=gerar-uma-chave-secreta-longa-e-aleatoria-aqui
DEBUG=False
ALLOWED_HOSTS=seu-projeto.railway.app,*.railway.app

# Email (obrigatório para notificações funcionarem)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail
DEFAULT_FROM_EMAIL=noreply@conhecesalguem.ao
BASE_URL=https://seu-projeto.railway.app
ADMIN_EMAIL=admin@conhecesalguem.ao

# Opcional: Para arquivos media em produção
# Use AWS S3 ou similar para arquivos grandes
```

### 4. **Gerar SECRET_KEY**

Execute no terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Use o resultado no `SECRET_KEY`

### 5. **Configurar Gmail para Emails**

1. Acesse sua conta Google
2. Ative "Verificação em 2 etapas"
3. Vá em "Senhas de app"
4. Gere uma senha para "Email"
5. Use essa senha no `EMAIL_HOST_PASSWORD`

### 6. **Deploy Automático**

A Railway detecta automaticamente:
- ✅ `Procfile` - como iniciar a aplicação
- ✅ `requirements.txt` - dependências Python
- ✅ `runtime.txt` - versão do Python

### 7. **Configurar Domínio Customizado (Opcional)**

1. No painel Railway, vá em "Settings"
2. Clique em "Generate Domain" ou adicione domínio customizado
3. Atualize `ALLOWED_HOSTS` e `BASE_URL` com o novo domínio

### 8. **Configurar Build e Deploy**

A Railway automaticamente:
- Instala dependências do `requirements.txt`
- Roda migrações (`migrate`)
- Coleta arquivos estáticos (`collectstatic`)
- Inicia o servidor com Gunicorn

### 9. **Pós-Deploy**

Após o primeiro deploy bem-sucedido:

1. **Criar Superusuário:**
   - No painel Railway, vá em "Deployments"
   - Clique nos três pontos do deploy → "View Logs"
   - Ou use Railway CLI:
   ```bash
   railway run python manage.py createsuperuser
   ```

2. **Carregar Dados Iniciais:**
   ```bash
   railway run python manage.py loaddata fixtures/provinces.json
   railway run python manage.py loaddata fixtures/luanda_cities.json
   railway run python manage.py loaddata fixtures/luanda_neighborhoods.json
   railway run python manage.py loaddata fixtures/service_categories.json
   ```

### 10. **Testar**

- Acesse o domínio fornecido pela Railway
- Teste todas as funcionalidades
- Verifique se emails estão sendo enviados

---

## 🔧 Troubleshooting

### Problema: Migrações não rodam
**Solução**: Adicione `--noinput` no Procfile (já está lá)

### Problema: Static files não aparecem
**Solução**: Verifique se `whitenoise` está configurado (já está)

### Problema: Erro 500
**Solução**: 
- Verifique logs no Railway
- Confirme que `SECRET_KEY` está configurada
- Confirme que `DATABASE_URL` está correta

### Problema: Media files não funcionam
**Solução**: Para produção, configure AWS S3 ou use Railway Volume (para arquivos pequenos, whitenoise serve)

---

## 📊 Monitoramento

- **Logs**: Acesse "Deployments" → "View Logs"
- **Métricas**: Railway mostra CPU, RAM, Network
- **Database**: Use "PostgreSQL" → "Query" para acessar dados

---

## 💰 Custos

- **Free Tier**: $5 créditos grátis/mês
- PostgreSQL: ~$5/mês (pode usar free tier pequeno)
- Domínio customizado: $10/ano (opcional)

---

## ✅ Checklist Final

- [ ] Projeto criado na Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] SECRET_KEY gerada e configurada
- [ ] Email configurado (Gmail ou outro)
- [ ] Domínio configurado
- [ ] Deploy bem-sucedido
- [ ] Superusuário criado
- [ ] Dados iniciais carregados
- [ ] Funcionalidades testadas

---

**Boa sorte com o deploy! 🚀**

