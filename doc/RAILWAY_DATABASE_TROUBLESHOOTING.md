# Troubleshooting - Conexão com Banco de Dados no Railway

## 🔍 Problema: Script aguardando banco mas não conecta

### Possíveis Causas

1. **DATABASE_URL não configurada**
   - Verifique no Railway → Variables se `DATABASE_URL` existe
   - Railway geralmente cria automaticamente quando você adiciona PostgreSQL

2. **Banco PostgreSQL não foi criado/inicializado**
   - No Railway, você precisa criar um serviço PostgreSQL separado
   - O serviço web depende do serviço PostgreSQL

3. **Serviço PostgreSQL não está rodando**
   - Verifique se o serviço PostgreSQL está ativo
   - Railway inicializa serviços em ordem, mas pode haver delay

4. **Formato incorreto da DATABASE_URL**
   - Railway deve passar no formato: `postgresql://user:password@host:port/dbname`
   - Verifique logs do Railway para ver a DATABASE_URL

## ✅ Soluções

### 1. Verificar DATABASE_URL no Railway

1. Acesse seu projeto no Railway
2. Vá em **Variables**
3. Procure por `DATABASE_URL`
4. Se não existir:
   - Adicione serviço PostgreSQL (Data → PostgreSQL)
   - Railway criará `DATABASE_URL` automaticamente

### 2. Verificar Serviço PostgreSQL

1. No Railway, verifique se há serviço PostgreSQL
2. O serviço deve estar **Running**
3. Se não estiver, inicie o serviço

### 3. Verificar Dependências no railway.json

Certifique-se de que o serviço web depende do PostgreSQL:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "bash scripts/start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/",
    "healthcheckTimeout": 10
  }
}
```

**Importante**: Railway gerencia dependências automaticamente, mas você pode configurar no painel.

### 4. Aumentar Timeout

O script agora espera até 60 tentativas (2 minutos). Se ainda não conectar:

1. Verifique logs do PostgreSQL no Railway
2. Verifique se o hostname está correto
3. Railway usa hostname interno: `postgres.railway.internal` ou similar

### 5. Debug Manual

Adicione temporariamente ao `start.sh` para debug:

```bash
echo "🔍 Debug DATABASE_URL:"
echo "   DATABASE_URL existe: $([ -n "$DATABASE_URL" ] && echo "Sim" || echo "Não")"
if [ -n "$DATABASE_URL" ]; then
    echo "   Primeiros 50 chars: ${DATABASE_URL:0:50}..."
    echo "   Host: $(echo $DATABASE_URL | grep -oP '@\K[^:]+')"
fi
```

## 🔧 Configuração Recomendada no Railway

### Estrutura de Serviços:
1. **PostgreSQL** (serviço de dados)
2. **Web** (sua aplicação Django) - depende de PostgreSQL

### Variáveis de Ambiente:
- `DATABASE_URL` - Criada automaticamente pelo Railway quando PostgreSQL é adicionado
- Não precisa configurar manualmente!

### Healthcheck:
- O PostgreSQL precisa estar healthy antes do web iniciar
- Railway faz isso automaticamente se os serviços estão linkados

## 📊 Logs para Verificar

No Railway, verifique logs de:
1. **PostgreSQL service** - Deve mostrar "database system is ready"
2. **Web service** - Deve mostrar tentativas de conexão e erros

## 🚨 Se Nada Funcionar

### Fallback Temporário (NÃO recomendado para produção):

O script agora mostra mensagens mais detalhadas. Se o problema persistir:

1. Verifique se o PostgreSQL está realmente rodando
2. Verifique os logs do PostgreSQL para erros
3. Tente recriar o serviço PostgreSQL no Railway
4. Verifique se não há firewall/network blocking

### Contato Railway Support:
Se o problema persistir, pode ser issue do Railway. Contate suporte com:
- Logs do serviço PostgreSQL
- Logs do serviço Web
- Configuração de DATABASE_URL (oculta senha)

