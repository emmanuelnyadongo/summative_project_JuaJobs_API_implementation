# JuaJobs API

A comprehensive RESTful API for the JuaJobs gig economy platform, built with Django and Django REST Framework.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication, profiles for clients and workers
- **Job Management**: Post, search, apply, and manage gig jobs
- **Payment System**: Secure payment processing with M-Pesa integration
- **Review System**: User ratings and feedback
- **Notifications**: Real-time notifications for platform events
- **Location Services**: Geographical data and location-based features
- **Skills Management**: User skills and job requirements

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for clients, workers, and admins
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Caching**: Redis-based caching for improved performance
- **Filtering & Search**: Advanced filtering, searching, and sorting
- **Pagination**: Efficient data pagination
- **Rate Limiting**: API rate limiting for security
- **Mobile Money Integration**: M-Pesa payment gateway support

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite (development), PostgreSQL (production)
- **Caching**: Redis
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Payment**: M-Pesa integration
- **Testing**: pytest, coverage
- **Deployment**: Gunicorn, Whitenoise

## 📋 Prerequisites

- Python 3.8+
- pip
- Redis (for caching)
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/emmanuelnyadongo/summative_project_JuaJobs_API_implementation.git
   cd jua-jobs-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway (M-Pesa)
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_PASSKEY=your-mpesa-passkey
MPESA_ENVIRONMENT=sandbox

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Key Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/password/change/` - Change password
- `POST /api/auth/password/reset/` - Reset password

#### Users
- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `GET /api/users/me/` - Get current user profile

#### Jobs
- `GET /api/jobs/` - List jobs
- `POST /api/jobs/` - Create job (clients only)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `GET /api/jobs/search/` - Search jobs

#### Job Applications
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Apply for job (workers only)
- `GET /api/applications/{id}/` - Get application details
- `PATCH /api/applications/{id}/respond/` - Respond to application

#### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/{id}/` - Get payment details
- `POST /api/payments/mpesa/` - M-Pesa payment

#### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/{id}/` - Get review details
- `PATCH /api/reviews/{id}/respond/` - Respond to review

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Getting a Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Using a Token
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer your_access_token"
```

## 👥 User Types

### Client
- Can post jobs
- Can review workers
- Can manage job applications
- Can make payments

### Worker
- Can apply for jobs
- Can manage their profile and skills
- Can review clients
- Can receive payments

### Admin
- Can manage all users
- Can verify users and skills
- Can access admin panel
- Can view system statistics

## 🧪 Testing

Run tests with coverage:
```bash
# Install test dependencies
pip install pytest pytest-django coverage

# Run tests
pytest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 📊 Database Schema

### Core Models
- **User**: Extended user model with client/worker roles
- **Job**: Job postings with categories and requirements
- **JobApplication**: Applications from workers to jobs
- **Payment**: Financial transactions
- **Review**: User feedback and ratings
- **Notification**: System notifications
- **Location**: Geographical data
- **Skill**: Skills and user skill associations

## 🚀 Deployment

### Production Setup

1. **Set up production database**
   ```bash
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Set DEBUG=False**
   ```bash
   DEBUG=False
   ```

4. **Use production server**
   ```bash
   gunicorn jua_jobs.wsgi:application
   ```

### Docker Deployment
```bash
# Build image
docker build -t jua-jobs-api .

# Run container
docker run -p 8000:8000 jua-jobs-api
```

## 🔧 Development

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions and classes
- Write tests for new features

### Git Workflow
1. Create feature branch
2. Make changes
3. Write tests
4. Run tests
5. Create pull request

## 📝 API Examples

### Register a Client
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "client1",
    "email": "client1@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "client",
    "phone_number": "+254700000000",
    "country": "Kenya",
    "city": "Nairobi"
  }'
```

### Post a Job
```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Web Developer Needed",
    "description": "Looking for a skilled web developer...",
    "category": 1,
    "job_type": "fixed",
    "experience_level": "intermediate",
    "budget_min": 50000,
    "budget_max": 100000,
    "required_skills": ["Python", "Django", "React"],
    "is_remote": true,
    "location": "Nairobi, Kenya"
  }'
```

### Apply for a Job
```bash
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "job": 1,
    "cover_letter": "I am interested in this position...",
    "proposed_rate": 75000,
    "estimated_duration": 40
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added M-Pesa integration
- **v1.2.0** - Enhanced search and filtering
- **v1.3.0** - Added notification system

## 🏗️ Architecture

The API follows a layered architecture:
- **Models**: Data layer with Django ORM
- **Serializers**: Data transformation layer
- **Views**: Business logic layer
- **URLs**: Routing layer
- **Permissions**: Security layer

## 🔒 Security Features

- JWT authentication
- Role-based access control
- Input validation
- SQL injection protection
- XSS protection
- CSRF protection
- Rate limiting
- Secure password hashing

## 📈 Performance

- Database query optimization
- Redis caching
- Pagination
- Efficient serializers
- Background task processing
- CDN for static files

---

**JuaJobs API** - Empowering the gig economy in Africa and beyond. 
