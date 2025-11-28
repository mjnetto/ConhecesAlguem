#!/bin/bash
set -e

# Script de inicialização para Railway
# Aguarda o banco estar disponível, roda migrações e inicia o servidor

echo "🚀 Iniciando aplicação Django..."

# Função para aguardar o banco estar disponível
wait_for_db() {
    echo "⏳ Aguardando banco de dados estar disponível..."
    echo "   DATABASE_URL configurada: $([ -n "$DATABASE_URL" ] && echo "Sim" || echo "Não")"
    max_attempts=60  # Aumentado para 60 tentativas (2 minutos)
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Testa conexão com mensagem de erro mais detalhada
        python_result=$(python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
    from django.db import connection
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('OK')
    sys.exit(0)
except Exception as e:
    print(f'Erro: {str(e)}')
    sys.exit(1)
" 2>&1)
        
        if [ $? -eq 0 ]; then
            echo "✅ Banco de dados disponível!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ $((attempt % 5)) -eq 0 ]; then
            # Mostra erro detalhado a cada 5 tentativas
            echo "   Tentativa $attempt/$max_attempts - Erro: $(echo "$python_result" | tail -1)"
        else
            echo "   Tentativa $attempt/$max_attempts - Banco ainda não disponível, aguardando..."
        fi
        sleep 2
    done
    
    echo "❌ Erro: Não foi possível conectar ao banco de dados após $max_attempts tentativas"
    echo "   Último erro: $(python -c "import os, sys, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from django.db import connection; connection.ensure_connection()" 2>&1 | tail -3)"
    echo ""
    echo "💡 Verifique:"
    echo "   - DATABASE_URL está configurada no Railway?"
    echo "   - Serviço PostgreSQL está rodando?"
    echo "   - As variáveis de ambiente estão corretas?"
    
    # Em produção, tenta continuar com SQLite como fallback (não recomendado, mas evita crash)
    if [ -z "$DATABASE_URL" ]; then
        echo "⚠️  DATABASE_URL não configurada. Usando SQLite (não recomendado para produção)."
        return 0
    fi
    
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

