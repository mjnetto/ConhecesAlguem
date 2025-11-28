# 🔧 Troubleshooting - Railway Deploy

## Problemas Comuns e Soluções

### ❌ Erro: "could not translate host name 'postgres.railway.internal' to address"

**Problema**: O Django está tentando conectar ao banco durante o build stage, quando o banco ainda não está disponível.

**Solução**: 
1. ✅ Usar o script `scripts/start.sh` que aguarda o banco estar disponível
2. ✅ O `railway.json` está configurado para usar `bash scripts/start.sh`
3. ✅ O script aguarda até 60 segundos (30 tentativas x 2s) pelo banco

**Se ainda ocorrer**:
- Verifique se o PostgreSQL está adicionado ao projeto Railway
- Verifique se a variável `DATABASE_URL` está configurada (é automática quando adiciona PostgreSQL)
- O script continua mesmo se migrações falharem (tenta novamente na próxima inicialização)

---

### ⚠️ Aviso: "The directory '/app/static' in STATICFILES_DIRS does not exist"

**Problema**: O Django está procurando uma pasta `/app/static` que não existe.

**Solução**: Isso é apenas um aviso e não impede o funcionamento. Se quiser remover:

1. Verifique `settings.py` - procure por `STATICFILES_DIRS`
2. Se a pasta não existir e não for necessária, remova da configuração ou crie a pasta vazia

**Nota**: Para produção, arquivos estáticos devem estar em `STATIC_ROOT` (coletados pelo `collectstatic`), não em `STATICFILES_DIRS`.

---

### ❌ Erro: Static files não aparecem

**Problema**: CSS, JS e imagens não carregam.

**Solução**:
1. Verifique se `whitenoise` está no `requirements.txt` ✅
2. Verifique se `WhiteNoiseMiddleware` está em `MIDDLEWARE` ✅
3. Verifique se `collectstatic` está rodando (ver logs)
4. No Railway, verifique os logs do deploy para ver se `collectstatic` executou

---

### ❌ Erro: Migrações não rodam

**Problema**: As migrações não são executadas automaticamente.

**Solução**:
- O script `start.sh` roda migrações automaticamente quando o serviço inicia
- Se precisar rodar manualmente:
  ```bash
  railway run python manage.py migrate
  ```

---

### ❌ Erro: "No module named 'X'"

**Problema**: Dependência faltando.

**Solução**:
1. Verifique se está no `requirements.txt`
2. Faça push das mudanças
3. Railway reinstala dependências no próximo deploy

---

### ⏱️ Deploy muito lento

**Possíveis causas**:
- `collectstatic` demorando muito (muitos arquivos estáticos)
- Build demorando (muitas dependências)

**Soluções**:
- Otimize imagens estáticas
- Use CDN para arquivos estáticos grandes (futuro)
- Verifique se não está incluindo `node_modules` ou outras pastas grandes no repositório

---

### 🔍 Como verificar logs

1. No Railway dashboard → seu projeto
2. Vá em **Deployments**
3. Clique no deployment mais recente
4. Veja as abas:
   - **Build Logs**: Logs do build
   - **Deploy Logs**: Logs do runtime
   - **Metrics**: CPU, memória, etc.

---

### 🆘 Comandos úteis

```bash
# Ver logs em tempo real
railway logs

# Rodar comando no ambiente Railway
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py loaddata fixtures/...

# Conectar ao shell Django
railway run python manage.py shell
```

---

### ✅ Checklist de Diagnóstico

Quando algo der errado:

- [ ] PostgreSQL está rodando e conectado?
- [ ] `DATABASE_URL` está nas variáveis de ambiente?
- [ ] `SECRET_KEY` está configurada?
- [ ] `DEBUG=False` em produção?
- [ ] `ALLOWED_HOSTS` inclui o domínio Railway?
- [ ] Dependências estão no `requirements.txt`?
- [ ] Scripts têm permissão de execução (`chmod +x`)?
- [ ] Logs mostram algum erro específico?

---

**Última atualização**: Após configuração do `railway.json` e `scripts/start.sh`

