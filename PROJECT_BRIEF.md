# Conheces Alguém? - MVP Technical Brief

## Project Overview

**Conheces Alguém?** is a TaskRabbit-style service marketplace platform designed specifically for the Angolan market. The platform connects clients with local professionals for various home services and tasks.

**Project Status:** MVP (Phase 1)  
**Target Market:** Angola  
**Platform Type:** Web Application (Mobile app planned for Phase 2)

---

## Table of Contents

1. [MVP Features (Phase 1)](#mvp-features-phase-1)
2. [Advanced Features (Future)](#advanced-features-future)
3. [Tech Stack](#tech-stack)
4. [Architecture Overview](#architecture-overview)
5. [Core Features Specification](#core-features-specification)
6. [Pre-loaded Data (Fixtures)](#pre-loaded-data-fixtures)
7. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
8. [Development Guidelines](#development-guidelines)
9. [Deployment Strategy](#deployment-strategy)

---

## MVP Features (Phase 1)

### 1. TaskRabbit-Style Homepage
- Service category cards with icons
- Visual, card-based layout
- Quick service selection interface
- Responsive design for mobile and desktop

### 2. 3-Step Booking Flow
**Step 1: Service Selection**
- Select service category/subcategory
- Task-specific details entry

**Step 2: Location Selection**
- Province selection (18 pre-loaded provinces)
- City selection (Luanda neighborhoods pre-loaded)
- Address entry (optional text field)

**Step 3: Professional Selection & Booking**
- View available professionals (filtered by location)
- Select professional
- Confirm booking details
- Submit booking request

### 3. Professional Registration
- Phone number (primary identifier)
- Personal information (name, email)
- **NIF (Tax ID)** - stored without validation
- **IBAN** - for payment processing
- **Portfolio** - image uploads and descriptions
- Service categories they offer
- Service areas (provinces/cities)
- Profile picture

### 4. Admin Activation System
- Professionals register with IBAN
- Admin manually verifies IBAN payment received
- Admin activates professional account via Django Admin
- Professionals receive notification upon activation
- Only activated professionals appear in search results

### 5. Reviews System
- Reviews linked to completed bookings only
- Rating system (1-5 stars)
- Written reviews/comments
- Display on professional profile
- Review aggregation (average rating, total reviews)

### 6. Pre-loaded Location Data
- **18 Angolan Provinces** (fixed list)
- **Luanda Neighborhoods** (10 pre-loaded)
- Dropdown/select fields (no free text)

### 7. Footer
- WhatsApp support link/button
- Social media links (Facebook, Instagram, LinkedIn)
- Mobile app download links (when available)
- Contact information
- Terms & Privacy links

---

## Advanced Features (Future)

### Phase 2 Features (Not in MVP)
- **In-App Chat**: Real-time messaging between clients and professionals
- **Automated Payments**: Integration with M-Pesa, Unitel Money APIs
- **Professional Tiers**: Bronze → Silver → Gold → Diamante levels
- **Sponsored Listings**: 24-hour top placement promotion system
- **Dispute Resolution**: Admin dashboard for handling disputes
- **Mobile App**: React Native iOS/Android application
- **Push Notifications**: Booking updates, messages
- **Multi-language Support**: Portuguese (primary), local languages
- **Analytics Dashboard**: For professionals to track bookings/earnings

---

## Tech Stack

### Backend
- **Framework**: Django 4.2+ (Python 3.11+)
  - Batteries included
  - Built-in admin panel
  - i18n support ready
  - Security features
  - ORM for database management

### Frontend
- **Templates**: Django Templates
- **Styling**: Tailwind CSS
- **JavaScript**: Vanilla JS (no framework for MVP)
- **Responsive**: Mobile-first design

### Database
- **Production**: PostgreSQL 14+
- **Development**: PostgreSQL via Docker

### Authentication
- **Method**: Phone number only
- **Verification**: Manual WhatsApp code (no SMS API initially)
- **No Password**: Clients don't need passwords for browsing/booking

### Payments
- **Phase 1**: Manual IBAN transfer verification
- **Phase 2**: M-Pesa, Unitel Money API integration

### Deployment
- **Platform**: Railway or Render (free tiers available)
- **Static Files**: Whitenoise or CDN
- **Media Files**: AWS S3 or similar (for portfolio images)

### Development Tools
- **Version Control**: Git
- **Package Management**: pip, requirements.txt
- **Environment**: python-dotenv for config
- **Testing**: Django TestCase, pytest

---

## Architecture Overview

### Project Structure
```
conheces-alguem/
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile (optional)
├── docker-compose.yml (for local PostgreSQL)
├── README.md
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py (Client, Professional)
│   ├── views.py
│   ├── forms.py
│   └── admin.py
├── services/
│   ├── models.py (Category, Subcategory, Service)
│   ├── views.py
│   └── fixtures/
├── bookings/
│   ├── models.py (Booking)
│   ├── views.py
│   └── forms.py
├── reviews/
│   ├── models.py (Review)
│   └── views.py
├── locations/
│   ├── models.py (Province, City, Neighborhood)
│   └── fixtures/
└── templates/
    ├── base.html
    ├── home.html
    ├── accounts/
    ├── services/
    ├── bookings/
    └── reviews/
```

### Data Models

#### User Models
- **Client**: Phone number, name, email (optional)
- **Professional**: Phone number, name, email, NIF, IBAN, is_activated, portfolio, profile_picture

#### Service Models
- **Category**: Name, icon_url, description
- **Subcategory**: Name, category (FK), description
- **Service**: Professional (FK), category (FK), subcategory (FK), description, pricing

#### Location Models
- **Province**: Name (choices from fixed list)
- **City**: Name, province (FK)
- **Neighborhood**: Name (for Luanda), city (FK)

#### Booking Models
- **Booking**: Client (FK), Professional (FK), Service (FK), status, location, date, time, notes

#### Review Models
- **Review**: Booking (FK), rating, comment, created_at

---

## Core Features Specification

### Homepage
- **Layout**: Grid of service category cards
- **Each Card**: Category icon, name, brief description
- **Interaction**: Click to start booking flow
- **Design**: TaskRabbit-style, clean, modern

### Booking Flow
1. **Service Selection Page**
   - Category selection
   - Subcategory selection (if applicable)
   - Task description field
   - "Continue" button

2. **Location Selection Page**
   - Province dropdown (18 options)
   - City dropdown (filtered by province)
   - Neighborhood dropdown (for Luanda only)
   - Address line (optional text)
   - "Continue" button

3. **Professional Selection & Booking Page**
   - List of available professionals (filtered by location and service)
   - Professional cards showing:
     - Profile picture
     - Name
     - Rating (if available)
     - Number of reviews
     - Service area
   - Click professional to book
   - Booking form: date, time, special instructions
   - Submit booking

### Professional Registration
- **Form Fields**:
  - Phone number (required, unique)
  - Full name (required)
  - Email (optional)
  - NIF (required, text field, no validation)
  - IBAN (required, text field)
  - Profile picture (image upload)
  - Service categories (multi-select)
  - Service areas (provinces/cities, multi-select)
  - Portfolio images (multiple uploads)
  - Portfolio descriptions
- **Submission**: Creates professional account with `is_activated=False`
- **Notification**: Email/SMS to admin for review

### Admin Panel (Django Admin)
- **Professional Activation**:
  - List view showing pending professionals
  - IBAN verification checkbox
  - Manual activation toggle
  - Notes field for admin use
- **Booking Management**:
  - View all bookings
  - Filter by status
  - Update booking status
- **Review Moderation**:
  - Approve/reject reviews
  - Edit/delete reviews if needed

### Reviews System
- **Access**: Only clients who completed bookings can review
- **Form**: Rating (1-5 stars), comment text
- **Display**: On professional profile page
- **Aggregation**: Show average rating and total count

---

## Pre-loaded Data (Fixtures)

### 1. Provinces (18)
```python
PROVINCES = [
    "Bengo",
    "Benguela",
    "Bié",
    "Cabinda",
    "Cuando Cubango",
    "Cuanza Norte",
    "Cuanza Sul",
    "Cunene",
    "Huambo",
    "Huíla",
    "Luanda",
    "Lunda Norte",
    "Lunda Sul",
    "Malanje",
    "Moxico",
    "Namibe",
    "Uíge",
    "Zaire"
]
```

### 2. Luanda Neighborhoods
```python
LUANDA_NEIGHBORHOODS = [
    "Talatona",
    "Viana",
    "Sambizanga",
    "Maianga",
    "Rangel",
    "Ingombotas",
    "Palanca",
    "Cazenga",
    "Kilamba",
    "Nova Lisboa"
]
```

### 3. Service Categories with Icons
```python
SERVICE_CATEGORIES = [
    {
        "name": "Furniture Assembly",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/2zLfFEV2MrXbcska0MocE7/32575342bd9f30397d58ccb663c71744/Homepage_Assembly.png?w=3840&q=75&fm=webp",
        "description": "Professional furniture assembly services"
    },
    {
        "name": "Wall Mounting",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/3yZJxfcMurN3fYgm2VIw3v/1f0aee924e621fd5e2684f01f92ca7b2/Mount_TV.jpg?w=3840&q=75&fm=webp",
        "description": "TV and wall mounting services"
    },
    {
        "name": "Cleaning",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/51s0CVltl03F7bOfy31VXB/8a5adaf0c64e789c7f202329724806c0/Home_Apartment_Cleaning.jpg?w=3840&q=75&fm=webp",
        "description": "Home and apartment cleaning services"
    },
    {
        "name": "Plumbing",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/2vw8Ct7BWBT12032WBzVyf/5332c4b1fc0b678d442c64307f31c2ae/AdobeStock_197426992.jpeg?w=3840&q=75&fm=webp",
        "description": "Professional plumbing services"
    },
    {
        "name": "Electrical",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/BUqnE9Sgc6YHLGISWe04H/31c63bdb1bc70d72161e4327594c6629/Electrical_Help.jpg?w=3840&q=75&fm=webp",
        "description": "Electrical repair and installation"
    },
    {
        "name": "Moving",
        "icon_url": "https://images.ctfassets.net/vwt5n1ljn95x/5RdOpgNLV7GFgjHegMSn4S/4da60b993bc3b03fcef4d19645c38e59/Help_Moving.jpg?w=3840&q=75&fm=webp",
        "description": "Moving and relocation services"
    }
]
```

### 4. Service Tree Structure
```
Category: Electrodomésticos (Appliances)
  ├── Subcategory: Máquinas de Lavar (Washing Machines)
  │     ├── Brand: LG
  │     ├── Brand: Samsung
  │     └── Brand: Beko
  ├── Subcategory: Frigoríficos (Refrigerators)
  │     ├── Brand: LG
  │     └── Brand: Samsung
  └── Subcategory: Fogões (Stoves)
        └── Brand: Electrolux
```

**Note**: For MVP, focus on the main 6 categories. Service tree (brands) can be added incrementally.

---

## Common Pitfalls to Avoid

### ❌ Don't Do These

1. **Password-Based Login for Clients**
   - Clients should book without creating accounts
   - Phone number is sufficient for identification
   - Only professionals need accounts

2. **Free-Text Location Fields**
   - Always use dropdown/select fields
   - Pre-load provinces and cities
   - No manual location entry that could cause data inconsistency

3. **NIF Validation**
   - No public NIF validation API exists in Angola
   - Just store the NIF as text
   - Don't attempt validation or checksum

4. **Public Professional List**
   - Don't expose a public directory/list of all professionals
   - Only show professionals in booking flow results
   - Prevents scraping and protects professional data

5. **Generic Booking Flow**
   - Keep it task-specific (like TaskRabbit)
   - Don't make it too generic
   - Focus on specific service categories

### ✅ Do These

1. **Task-Specific Booking**
   - Each booking is for a specific service/task
   - Clear service selection upfront

2. **Django Admin for Activation**
   - Use built-in Django Admin
   - No need for custom admin dashboard in MVP
   - Manual verification and activation

3. **Pre-loaded Location Data**
   - Use fixtures or migration data
   - Ensure consistency across the platform

4. **Mobile-First Design**
   - Most users will access via mobile
   - Responsive design is critical

5. **WhatsApp Integration**
   - Use WhatsApp links in footer
   - Consider WhatsApp Business API for notifications (Phase 2)

---

## Development Guidelines

### Code Standards
- **PEP 8** compliance for Python
- **Django Best Practices**: Use class-based views, models, forms
- **Security**: Use Django's built-in security features
- **Error Handling**: Proper exception handling and user feedback

### Database Considerations
- Use migrations for schema changes
- Create fixtures for initial data (provinces, categories)
- Index frequently queried fields (location, service category)

### Authentication Flow
1. Client enters phone number
2. System sends WhatsApp code (manual initially)
3. Client enters code
4. Client can browse and book services
5. Professionals require full registration with NIF/IBAN

### Image Handling
- Use Pillow for image processing
- Set max upload sizes (e.g., 5MB for profile, 10MB for portfolio)
- Store in media/ directory (or S3 in production)
- Generate thumbnails for listings

### Testing Requirements
- Unit tests for models
- Integration tests for booking flow
- Form validation tests
- Admin functionality tests

### Localization
- Prepare for Portuguese (pt-AO)
- Use Django's i18n framework
- All user-facing strings should be translatable
- Currency: Kwanza (AOA) - format: 1.000,00 AOA

---

## Deployment Strategy

### Development Environment
1. Set up virtual environment
2. Install dependencies from `requirements.txt`
3. Run PostgreSQL via Docker:
   ```bash
   docker-compose up -d postgres
   ```
4. Run migrations: `python manage.py migrate`
5. Load fixtures: `python manage.py loaddata initial_data`
6. Create superuser: `python manage.py createsuperuser`
7. Run dev server: `python manage.py runserver`

### Production Deployment (Railway/Render)
1. Set up PostgreSQL database
2. Set environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL`
   - `ALLOWED_HOSTS`
   - `AWS_ACCESS_KEY_ID` (if using S3)
   - `AWS_SECRET_ACCESS_KEY`
3. Run migrations
4. Load fixtures
5. Collect static files: `python manage.py collectstatic`
6. Set up static file serving (Whitenoise or CDN)

### Environment Variables Template
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email (optional for MVP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password

# AWS S3 (for media files in production)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

---

## Project Timeline (Estimated)

### Week 1-2: Setup & Core Models
- Project setup
- Database models
- Django Admin configuration
- Location fixtures

### Week 3-4: Authentication & Registration
- Phone-based auth for clients
- Professional registration
- Admin activation workflow

### Week 5-6: Service & Booking System
- Service categories and fixtures
- Booking flow (3 steps)
- Professional selection logic

### Week 7: Reviews System
- Review models and forms
- Review display on profiles
- Review aggregation

### Week 8: Frontend & Styling
- Homepage design
- Booking flow UI
- Responsive design
- Tailwind CSS integration

### Week 9: Testing & Bug Fixes
- Comprehensive testing
- Bug fixes
- Performance optimization

### Week 10: Deployment
- Production setup
- Final testing
- Launch preparation

---

## Success Metrics (Post-MVP)

- Number of registered professionals
- Number of completed bookings
- Average rating of professionals
- User retention rate
- Booking completion rate
- Response time (professional to client)

---

## Support & Resources

### Documentation References
- Django Documentation: https://docs.djangoproject.com/
- Tailwind CSS: https://tailwindcss.com/
- PostgreSQL: https://www.postgresql.org/docs/

### Contact
- **WhatsApp Support**: [To be configured]
- **Email**: [To be configured]
- **Project Repository**: [To be configured]

---

## Notes for Development Team

1. **Start Simple**: MVP should focus on core functionality. Avoid feature creep.

2. **Angola-Specific Considerations**:
   - Phone number format: +244 XX XXX XXXX
   - Currency: Kwanza (AOA)
   - Language: Portuguese (Angola variant)
   - Payment methods: IBAN transfers are common

3. **Scalability**: Design with growth in mind, but don't over-engineer for MVP.

4. **Security**: 
   - Validate all user inputs
   - Protect against SQL injection (Django ORM handles this)
   - CSRF protection (Django default)
   - XSS protection (Django templates escape by default)

5. **Performance**:
   - Use database indexes
   - Optimize queries (use select_related, prefetch_related)
   - Cache frequently accessed data (locations, categories)

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Status**: Ready for Development


