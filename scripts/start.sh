#!/bin/bash
set -e

# Script de inicialização para Railway
# Aguarda o banco estar disponível, roda migrações e inicia o servidor

# Evita loops - apenas roda uma vez
if [ -n "$RAILWAY_STARTED" ]; then
    echo "⚠️  Script já foi executado. Ignorando execução duplicada."
    exit 0
fi
export RAILWAY_STARTED=1

echo "🚀 Iniciando aplicação Django..."
echo "   Timestamp: $(date)"

# Função para aguardar o banco estar disponível
wait_for_db() {
    echo "⏳ Aguardando banco de dados estar disponível..."
    if [ -n "$DATABASE_URL" ]; then
        # Mostra info sem senha
        DB_INFO=$(echo "$DATABASE_URL" | sed 's/:[^:@]*@/:***@/')
        echo "   DATABASE_URL: ${DB_INFO:0:80}..."
    else
        echo "   ⚠️  DATABASE_URL não configurada!"
    fi
    
    max_attempts=60  # 60 tentativas = 2 minutos
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Testa conexão
        python_result=$(python3 -c "
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
    from django.db import connection
    from django.conf import settings
    
    # Mostra configuração do banco (sem senha)
    db_config = settings.DATABASES['default']
    print(f'🔍 Tentando conectar: {db_config[\"HOST\"]}:{db_config[\"PORT\"]}/{db_config[\"NAME\"]}')
    
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Conexão OK')
    sys.exit(0)
except Exception as e:
    import traceback
    error_msg = str(e)
    print(f'❌ Erro: {error_msg[:200]}')
    sys.exit(1)
" 2>&1)
        
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "$python_result" | grep -E "(🔍|✅)"
            echo "✅ Banco de dados disponível!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        
        # Mostra erro detalhado (primeira tentativa e a cada 5)
        if [ $attempt -eq 1 ] || [ $((attempt % 5)) -eq 0 ]; then
            echo ""
            echo "   Tentativa $attempt/$max_attempts"
            echo "$python_result" | tail -3 | sed 's/^/   /'
        else
            echo -n "."
        fi
        
        sleep 2
    done
    
    echo ""
    echo "❌ Erro: Não foi possível conectar ao banco após $max_attempts tentativas"
    echo ""
    echo "🔍 Última tentativa de diagnóstico:"
    python3 -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.conf import settings
db = settings.DATABASES['default']
print(f'   Engine: {db[\"ENGINE\"]}')
print(f'   Host: {db.get(\"HOST\", \"N/A\")}')
print(f'   Port: {db.get(\"PORT\", \"N/A\")}')
print(f'   Database: {db.get(\"NAME\", \"N/A\")}')
print(f'   User: {db.get(\"USER\", \"N/A\")}')
" 2>&1 | sed 's/^/   /'
    
    echo ""
    echo "💡 Possíveis causas:"
    echo "   1. Serviço PostgreSQL não está rodando no Railway"
    echo "   2. DATABASE_URL está incorreta ou mal formatada"
    echo "   3. Network/firewall bloqueando conexão"
    echo "   4. PostgreSQL ainda está inicializando"
    echo ""
    echo "📋 Verifique no Railway:"
    echo "   - Serviço PostgreSQL está 'Running'?"
    echo "   - Variables → DATABASE_URL existe?"
    echo "   - Logs do PostgreSQL mostram erros?"
    
    exit 1
}

# Aguarda o banco estar disponível (apenas se DATABASE_URL estiver configurada)
if [ -n "$DATABASE_URL" ]; then
    wait_for_db
else
    echo "⚠️  DATABASE_URL não configurada. Usando SQLite (modo desenvolvimento)."
fi

# Roda migrações (após garantir que o banco está disponível)
echo "📦 Executando migrações..."
if python manage.py migrate --noinput; then
    echo "✅ Migrações executadas com sucesso!"
else
    echo "❌ Erro ao executar migrações!"
    exit 1
fi

# Carrega dados iniciais (fixtures) apenas se não existirem
echo "📋 Verificando dados iniciais..."
if python manage.py shell -c "
import django
django.setup()
from locations.models import Province
from services.models import ServiceCategory
if Province.objects.count() == 0:
    print('Carregando províncias...')
    exit(1)
if ServiceCategory.objects.count() == 0:
    print('Carregando categorias de serviços...')
    exit(1)
exit(0)
" 2>/dev/null; then
    echo "✅ Dados iniciais já existem!"
    # Sincroniza categorias de serviços (cria as que faltam e atualiza as existentes)
    echo "🔄 Sincronizando categorias de serviços..."
    python manage.py sync_service_categories 2>/dev/null || echo "⚠️  Comando de sincronização não disponível"
else
    echo "📥 Carregando dados iniciais..."
    python manage.py loaddata fixtures/provinces.json || echo "⚠️  Províncias podem já existir"
    python manage.py loaddata fixtures/luanda_cities.json || echo "⚠️  Cidades podem já existir"
    python manage.py loaddata fixtures/luanda_neighborhoods.json || echo "⚠️  Bairros podem já existir"
    python manage.py loaddata fixtures/service_categories.json || echo "⚠️  Categorias podem já existir"
    echo "✅ Dados iniciais carregados!"
fi

# Coleta arquivos estáticos
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Inicia o servidor Gunicorn
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

