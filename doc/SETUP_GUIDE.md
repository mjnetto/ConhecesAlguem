# Setup Guide - Conheces Alguém?

Guia passo-a-passo para configurar o projeto do zero.

## 📋 Pré-requisitos

1. **Python 3.11+**
   ```bash
   python --version
   # Deve mostrar Python 3.11 ou superior
   ```

2. **PostgreSQL 14+** ou Docker
   ```bash
   # Verificar PostgreSQL
   psql --version
   
   # OU verificar Docker
   docker --version
   ```

3. **Git**
   ```bash
   git --version
   ```

---

## 🔧 Passo 1: Configurar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verificar que está ativo (deve mostrar o caminho do venv)
which python  # Linux/Mac
where python  # Windows
```

---

## 📦 Passo 2: Instalar Dependências

```bash
# Com o venv ativo, instalar pacotes
pip install -r requirements.txt

# Verificar instalação
pip list
```

---

## 🗄️ Passo 3: Configurar Base de Dados

### Opção A: Usar Docker (Recomendado)

```bash
# Iniciar PostgreSQL
docker-compose up -d db

# Verificar se está rodando
docker-compose ps

# Logs
docker-compose logs db
```

### Opção B: PostgreSQL Local

```bash
# Criar base de dados
createdb conheces_alguem

# OU usando psql
psql -U postgres
CREATE DATABASE conheces_alguem;
\q
```

---

## ⚙️ Passo 4: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env (use seu editor preferido)
nano .env
# ou
code .env
```

**Configurações mínimas no `.env`:**
```env
SECRET_KEY=seu-secret-key-aqui-gere-um-novo
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/conheces_alguem
```

**Para gerar um SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🏗️ Passo 5: Criar Projeto Django

```bash
# Se ainda não existe, criar projeto
django-admin startproject core .

# Verificar estrutura
ls -la
```

---

## 📱 Passo 6: Criar Apps Django

```bash
# Criar apps necessários
python manage.py startapp accounts
python manage.py startapp locations
python manage.py startapp services
python manage.py startapp bookings
python manage.py startapp reviews

# Adicionar apps ao INSTALLED_APPS em core/settings.py
```

**Adicionar ao `core/settings.py`:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'accounts',
    'locations',
    'services',
    'bookings',
    'reviews',
    
    # Third party
    'phonenumber_field',
    'crispy_forms',
    'crispy_bootstrap5',
]
```

---

## 🗃️ Passo 7: Configurar Modelos

1. **Copiar modelos** de `models_structure.py` para os respectivos `models.py`:
   - `locations/models.py` → Models: Province, City, Neighborhood
   - `accounts/models.py` → Models: Client, Professional, PortfolioItem
   - `services/models.py` → Models: ServiceCategory, ServiceSubcategory, ProfessionalService
   - `bookings/models.py` → Model: Booking
   - `reviews/models.py` → Model: Review

2. **Criar migrações:**
```bash
python manage.py makemigrations
```

3. **Aplicar migrações:**
```bash
python manage.py migrate
```

---

## 📊 Passo 8: Carregar Dados Iniciais

```bash
# Carregar províncias
python manage.py loaddata fixtures/provinces.json

# Carregar cidade de Luanda
python manage.py loaddata fixtures/luanda_cities.json

# Carregar bairros de Luanda
python manage.py loaddata fixtures/luanda_neighborhoods.json

# Carregar categorias de serviços
python manage.py loaddata fixtures/service_categories.json

# Verificar dados carregados
python manage.py shell
>>> from locations.models import Province
>>> Province.objects.count()  # Deve retornar 18
>>> from services.models import ServiceCategory
>>> ServiceCategory.objects.count()  # Deve retornar 6
```

---

## 👤 Passo 9: Criar Superusuário

```bash
python manage.py createsuperuser

# Seguir instruções:
# Username: admin
# Email: admin@example.com
# Password: [escolher senha segura]
```

---

## 🎨 Passo 10: Configurar Tailwind CSS (Opcional mas Recomendado)

```bash
# Instalar Tailwind CLI
npm install -D tailwindcss
npx tailwindcss init

# Configurar tailwind.config.js
# Adicionar caminhos dos templates:
content: ["./templates/**/*.html", "./static/**/*.js"]

# Adicionar ao base.html
# <script src="https://cdn.tailwindcss.com"></script>
# OU configurar build process
```

---

## ▶️ Passo 11: Rodar Servidor de Desenvolvimento

```bash
python manage.py runserver

# Abrir no navegador:
# http://localhost:8000
# http://localhost:8000/admin
```

---

## ✅ Verificação Final

### Checklist de Funcionamento

- [ ] Servidor Django inicia sem erros
- [ ] Admin panel acessível em `/admin`
- [ ] Consegue fazer login como superuser
- [ ] Províncias carregadas (18 no admin)
- [ ] Categorias de serviços carregadas (6 no admin)
- [ ] Consegue criar um Cliente no admin
- [ ] Consegue criar um Profissional no admin
- [ ] Database migrations aplicadas

### Testar Criação de Dados

```bash
python manage.py shell
```

```python
# Testar criação de Cliente
from accounts.models import Client
from phonenumber_field.phonenumber import PhoneNumber

client = Client.objects.create(
    phone_number=PhoneNumber.from_string("+244912345678", region="AO"),
    name="João Silva",
    is_verified=True
)
print(f"Cliente criado: {client}")

# Testar criação de Profissional
from accounts.models import Professional
from locations.models import Province

luanda = Province.objects.get(name="Luanda")
professional = Professional.objects.create(
    phone_number=PhoneNumber.from_string("+244923456789", region="AO"),
    name="Maria Santos",
    nif="123456789LA045",
    iban="AO06004400012345678910144",
    is_activated=False
)
professional.service_provinces.add(luanda)
print(f"Profissional criado: {professional}")

# Verificar dados
print(f"Total de províncias: {Province.objects.count()}")
print(f"Total de profissionais: {Professional.objects.count()}")
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Erro: "Database connection failed"
- Verificar se PostgreSQL está rodando
- Verificar DATABASE_URL no .env
- Testar conexão: `psql -U postgres -d conheces_alguem`

### Erro: "ModuleNotFoundError"
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro ao carregar fixtures
```bash
# Verificar formato JSON
python -m json.tool fixtures/provinces.json

# Se houver erro, verificar nomes dos models
python manage.py dumpdata locations.Province --indent 2
```

### Migrations não aplicam
```bash
# Resetar migrations (CUIDADO: apaga dados)
python manage.py migrate --run-syncdb

# OU recriar migrações
rm -rf */migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

---

## 📚 Próximos Passos

1. **Criar Views e URLs**
   - Homepage
   - Booking flow (3 steps)
   - Professional registration
   - Professional profile

2. **Criar Templates**
   - Base template com Tailwind
   - Homepage com cards de serviços
   - Booking forms
   - Professional profiles

3. **Implementar Autenticação**
   - Phone verification flow
   - WhatsApp code (manual inicialmente)

4. **Configurar Admin**
   - Customizar admin para Professionals
   - Adicionar filtros e busca
   - Actions para ativação em massa

5. **Testes**
   - Unit tests para models
   - Integration tests para booking flow

---

## 🆘 Suporte

Se encontrar problemas:
1. Verificar logs do Django
2. Verificar logs do PostgreSQL
3. Consultar `PROJECT_BRIEF.md` para especificações
4. Abrir issue no repositório

---

**Bom desenvolvimento! 🚀**

