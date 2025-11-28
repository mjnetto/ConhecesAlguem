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
    
    # Primeiro, tenta resolver o hostname
    if [ -n "$DATABASE_URL" ]; then
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        if [ -n "$DB_HOST" ]; then
            echo "   🔍 Verificando resolução DNS para: $DB_HOST"
            if getent hosts "$DB_HOST" >/dev/null 2>&1 || nslookup "$DB_HOST" >/dev/null 2>&1; then
                DB_IP=$(getent hosts "$DB_HOST" 2>/dev/null | awk '{print $1}' | head -1 || echo "N/A")
                echo "   ✅ Hostname resolve para: $DB_IP"
            else
                echo "   ⚠️  Hostname não resolve ainda (pode estar inicializando)"
            fi
        fi
    fi
    
    while [ $attempt -lt $max_attempts ]; do
        # Testa conexão
        python_result=$(python3 -c "
import os
import sys
import django
import socket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
    from django.db import connection
    from django.conf import settings
    
    # Mostra configuração do banco (sem senha)
    db_config = settings.DATABASES['default']
    host = db_config.get('HOST', 'N/A')
    port = db_config.get('PORT', 'N/A')
    db_name = db_config.get('NAME', 'N/A')
    
    print(f'🔍 Tentativa {sys.argv[1] if len(sys.argv) > 1 else \"?\"}: {host}:{port}/{db_name}')
    
    # Tenta resolver o hostname primeiro
    try:
        if host and host != 'N/A' and not host.startswith('/'):
            socket.gethostbyname(host)
            print(f'✅ DNS OK: {host} resolve')
    except socket.gaierror as e:
        print(f'⚠️  DNS Error: {host} não resolve - {str(e)}')
    
    # Tenta conectar
    connection.ensure_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Conexão estabelecida com sucesso!')
    sys.exit(0)
except Exception as e:
    import traceback
    error_type = type(e).__name__
    error_msg = str(e)
    print(f'❌ {error_type}: {error_msg}')
    # Mostra traceback completo apenas na primeira tentativa
    if len(sys.argv) > 1 and sys.argv[1] == '1':
        print('\\n📋 Traceback completo:')
        traceback.print_exc()
    sys.exit(1)
" "$((attempt + 1))" 2>&1)
        
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "$python_result"
            echo "✅ Banco de dados disponível!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        
        # Mostra erro detalhado sempre na primeira tentativa, depois a cada 5
        if [ $attempt -eq 1 ]; then
            echo ""
            echo "   ⚠️  Primeira tentativa falhou:"
            echo "$python_result" | sed 's/^/   /'
            echo ""
        elif [ $((attempt % 5)) -eq 0 ]; then
            echo ""
            echo "   Tentativa $attempt/$max_attempts"
            echo "$python_result" | grep -E "(🔍|❌|⚠️)" | tail -2 | sed 's/^/   /'
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

# Coleta estáticos primeiro (rápido, não precisa de DB completamente)
echo "📂 Coletando arquivos estáticos (inicial)..."
python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️  Erro ao coletar estáticos, continuando..."

# Inicia o servidor Gunicorn ANTES de migrações (healthcheck precisa funcionar rápido)
echo "🌐 Iniciando servidor Gunicorn..."
echo "   Porta: ${PORT:-8000}"
echo "   Host: 0.0.0.0"
echo "   Healthcheck: /health/"

# Inicia Gunicorn em background usando nohup para não terminar quando o script continuar
nohup gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload > /tmp/gunicorn.log 2>&1 &

GUNICORN_PID=$!
echo "   Gunicorn iniciado em background (PID: $GUNICORN_PID)"

# Aguarda alguns segundos para garantir que o servidor iniciou
echo "   Aguardando servidor inicializar..."
sleep 8

# Verifica se o processo ainda está rodando
if ! kill -0 $GUNICORN_PID 2>/dev/null; then
    echo "❌ Erro: Gunicorn parou inesperadamente!"
    echo "Últimas linhas do log:"
    tail -20 /tmp/gunicorn.log 2>/dev/null || echo "Log não disponível"
    exit 1
fi

# Testa se o servidor está respondendo
if curl -f -s http://localhost:${PORT:-8000}/health/ > /dev/null 2>&1; then
    echo "✅ Servidor respondendo! Healthcheck deve funcionar."
else
    echo "⚠️  Servidor pode ainda estar inicializando..."
fi
echo ""

# Agora executa setup (migrações, fixtures) - o servidor já está rodando
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
    # Não sai, continua - o servidor já está rodando
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

# Coleta arquivos estáticos novamente (caso tenha mudado)
echo "📂 Finalizando coleta de arquivos estáticos..."
python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️  Erro ao coletar estáticos, continuando..."

echo ""
echo "✅ Setup completo! Servidor rodando em background."
echo "   Para ver logs do Gunicorn: tail -f /tmp/gunicorn.log"
echo "   Aguardando processo principal..."

# Aguarda o processo Gunicorn (processo principal)
wait $GUNICORN_PID

