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
    # Atualiza imagens das categorias se necessário
    echo "🖼️  Verificando imagens das categorias..."
    python manage.py shell < scripts/update_category_images.py 2>/dev/null || echo "⚠️  Script de atualização de imagens não encontrado ou erro ao executar"
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

