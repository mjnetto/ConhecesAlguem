# Quick Start - Conheces Alguém?

## ✅ Setup Completo!

O projeto está configurado e pronto para uso.

## 🚀 Como Iniciar (Forma Mais Fácil)

### Usar o Script de Inicialização:
```bash
./start.sh
```

Este script vai:
- ✅ Criar/ativar o ambiente virtual
- ✅ Instalar dependências se necessário
- ✅ Verificar e iniciar PostgreSQL
- ✅ Aplicar migrações
- ✅ Iniciar o servidor Django

---

## 🚀 Como Iniciar (Manual)

### 1. Ativar Ambiente Virtual
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Iniciar PostgreSQL (Docker)
```bash
docker-compose up -d db
```

### 3. Rodar o Servidor Django
```bash
python manage.py runserver
```

### 4. Acessar a Aplicação

- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`

## 📊 Dados Carregados

✅ **18 Províncias** de Angola  
✅ **1 Cidade** (Luanda)  
✅ **10 Bairros** de Luanda  
✅ **6 Categorias de Serviços** com ícones

## 🗄️ Database Status

- ✅ Migrações aplicadas
- ✅ Dados iniciais carregados
- ✅ Superusuário criado

## 📁 Estrutura Criada

```
✅ Django Project (core/)
✅ Apps: accounts, locations, services, bookings, reviews
✅ Modelos completos
✅ Django Admin configurado
✅ Templates básicos (Homepage + Base)
✅ PostgreSQL rodando via Docker
```

## 🔧 Comandos Úteis

### Ativar/Desativar Venv
```bash
# Ativar
source venv/bin/activate

# Desativar
deactivate
```

### Verificar se venv está ativo
```bash
which python  # Deve mostrar o caminho do venv
```

### Instalar nova dependência
```bash
source venv/bin/activate
pip install nome-do-pacote
pip freeze > requirements.txt  # Atualizar requirements.txt
```

### Criar superusuário
```bash
source venv/bin/activate
python manage.py createsuperuser
```

---

**Status**: ✅ Pronto para desenvolvimento! 🎉
