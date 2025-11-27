#!/bin/bash

# Script para iniciar o projeto Conheces Alguém?

echo "🚀 Iniciando Conheces Alguém?..."
echo ""

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências se necessário
if [ ! -f "venv/.deps_installed" ]; then
    echo "📥 Instalando dependências..."
    pip install -q -r requirements.txt
    touch venv/.deps_installed
fi

# Verificar se PostgreSQL está rodando
echo "🗄️  Verificando PostgreSQL..."
if ! docker-compose ps db | grep -q "Up"; then
    echo "   Iniciando PostgreSQL..."
    docker-compose up -d db
    sleep 3
fi

# Rodar migrações se necessário
echo "🔄 Verificando migrações..."
python manage.py migrate --check || python manage.py migrate

# Iniciar servidor
echo ""
echo "✅ Tudo pronto!"
echo "🌐 Servidor iniciando em http://localhost:8000"
echo "👤 Admin: http://localhost:8000/admin (admin/admin123)"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

python manage.py runserver

