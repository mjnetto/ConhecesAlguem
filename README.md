# Conheces Alguém? 🛠️

**TaskRabbit-style service marketplace for Angola**

Conecta clientes com profissionais locais para serviços domésticos e tarefas diversas.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Docker)
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Conheces Alguém?"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL with Docker** (recommended for development)
   ```bash
   docker-compose up -d db
   ```
   
   Or use a local PostgreSQL instance:
   ```bash
   createdb conheces_alguem
   ```

5. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Load initial data**
   ```bash
   python manage.py loaddata fixtures/provinces.json
   python manage.py loaddata fixtures/luanda_cities.json
   python manage.py loaddata fixtures/luanda_neighborhoods.json
   python manage.py loaddata fixtures/service_categories.json
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Frontend: http://localhost:8000
    - Admin: http://localhost:8000/admin

---

## 📁 Project Structure

```
conheces-alguem/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── README.md
├── PROJECT_BRIEF.md
├── models_structure.py          # Complete model definitions
├── fixtures/                    # Initial data
│   ├── provinces.json
│   ├── luanda_cities.json
│   ├── luanda_neighborhoods.json
│   └── service_categories.json
├── core/                        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                    # Client & Professional models
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── admin.py
├── locations/                   # Province, City, Neighborhood
│   ├── models.py
│   └── fixtures/
├── services/                    # Service categories & subcategories
│   ├── models.py
│   ├── views.py
│   └── fixtures/
├── bookings/                    # Booking system
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── reviews/                     # Review system
│   ├── models.py
│   └── views.py
└── templates/                   # Django templates
    ├── base.html
    ├── home.html
    └── ...
```

---

## 🗄️ Database Models

### Core Models

- **Client**: Phone-based user authentication
- **Professional**: Service providers with NIF/IBAN verification
- **Booking**: Connects clients with professionals
- **Review**: Linked to completed bookings only
- **ServiceCategory**: Main service types (Cleaning, Plumbing, etc.)
- **Province/City/Neighborhood**: Location hierarchy

See `models_structure.py` for complete model definitions.

---

## 🔧 Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
flake8 .
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Fixtures

```bash
python manage.py dumpdata app.ModelName --indent 2 > fixtures/model_name.json
```

---

## 🌍 Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/conheces_alguem

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# AWS S3 (Production - Optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
```

---

## 📋 Features (MVP)

✅ TaskRabbit-style homepage  
✅ 3-step booking flow  
✅ Professional registration with NIF/IBAN  
✅ Admin activation system  
✅ Reviews linked to bookings  
✅ Pre-loaded Angolan provinces & Luanda neighborhoods  
✅ Footer with WhatsApp support  

See `PROJECT_BRIEF.md` for complete feature documentation.

---

## 🚢 Deployment

### Railway

1. Connect your GitHub repository
2. Add PostgreSQL service
3. Set environment variables
4. Deploy

### Render

1. Create new Web Service
2. Connect repository
3. Add PostgreSQL database
4. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Set start command: `gunicorn core.wsgi:application`
6. Set environment variables

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...
```

---

## 📱 API Endpoints (Future)

The MVP uses Django templates, but API endpoints can be added for future mobile app:

- `/api/bookings/` - List/Create bookings
- `/api/professionals/` - List professionals (filtered)
- `/api/reviews/` - List/Create reviews
- `/api/auth/verify-phone/` - Phone verification

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

[Add your license here]

---

## 📞 Support

- **WhatsApp**: [Your WhatsApp number]
- **Email**: [Your email]
- **Documentation**: See `PROJECT_BRIEF.md`

---

## 🎯 Roadmap

### Phase 1 (MVP) - Current
- ✅ Core booking system
- ✅ Professional registration
- ✅ Review system

### Phase 2 - Future
- 🔄 In-app chat
- 🔄 Automated payments (M-Pesa, Unitel Money)
- 🔄 Professional tiers
- 🔄 Mobile app (React Native)
- 🔄 Push notifications

---

**Made with ❤️ for Angola**

