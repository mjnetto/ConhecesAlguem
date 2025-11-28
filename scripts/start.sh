#!/bin/bash
set -e

# Script de inicialização para Railway
# Aguarda o banco estar disponível, roda migrações e inicia o servidor

echo "🚀 Iniciando aplicação Django..."

# Função para aguardar o banco estar disponível
wait_for_db() {
    echo "⏳ Aguardando banco de dados estar disponível..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
            echo "✅ Banco de dados disponível!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "   Tentativa $attempt/$max_attempts - Banco ainda não disponível, aguardando..."
        sleep 2
    done
    
    echo "❌ Erro: Não foi possível conectar ao banco de dados após $max_attempts tentativas"
    exit 1
}

# Aguarda o banco estar disponível (apenas se DATABASE_URL estiver configurada)
if [ -n "$DATABASE_URL" ]; then
    wait_for_db
fi

# Roda migrações (após garantir que o banco está disponível)
echo "📦 Executando migrações..."
if python manage.py migrate --noinput; then
    echo "✅ Migrações executadas com sucesso!"
else
    echo "❌ Erro ao executar migrações!"
    exit 1
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

