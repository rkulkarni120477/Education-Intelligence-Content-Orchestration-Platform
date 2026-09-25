# Backend Implementation Guide

## Overview
Complete backend implementation for the Academian Education Platform with authentication, user management, email service, and database integration.

---

## 📋 What Was Implemented

### 1. **Database Models**

#### Enhanced User Model
```python
- id: UUID (primary key)
- email: Unique email address
- username: Unique username
- full_name: Full name
- hashed_password: Bcrypt hashed password
- is_active: Account active status
- is_admin: Admin privileges
- email_verified: Email verification status
- email_verification_token: Token for email verification
- password_reset_token: Token for password reset
- password_reset_token_expires: Token expiration time
- last_login: Last login timestamp
- created_at, updated_at: Timestamps
```

#### New Models
- **UserPreferences**: User settings and notification preferences
- **ApiKey**: API key management for programmatic access
- **UserSession**: Active sessions tracking

### 2. **Authentication System**

#### Core Functions (auth/auth.py)
- `verify_password()`: Check password against hash
- `get_password_hash()`: Hash password with bcrypt
- `create_access_token()`: Generate JWT token
- `decode_token()`: Validate and decode JWT
- `authenticate_user()`: Verify credentials
- `create_user()`: Create new user account
- `generate_password_reset_token()`: Create secure reset token
- `verify_password_reset_token()`: Validate reset token
- `reset_password()`: Update password
- `generate_email_verification_token()`: Create email verification token
- `verify_email_token()`: Verify and mark email as verified
- `update_last_login()`: Track login activity

### 3. **Email Service**

#### EmailService Class (services/email_service.py)
```python
Features:
- SMTP email sending (Gmail, AWS SES, etc.)
- HTML email templates
- Text fallback support
- Logging and error handling
```

#### Email Templates
1. **Password Reset Email**
   - 24-hour expiration link
   - Security warnings
   - Clear instructions

2. **Welcome Email**
   - Account verification link
   - Feature overview
   - Getting started guide

3. **Workflow Notifications**
   - Status updates (started, completed, failed)
   - Detailed information
   - Dashboard link

4. **Weekly Digest**
   - Activity summary
   - Workflow statistics
   - Actionable insights

### 4. **API Endpoints**

#### Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "secure_password"
}

Response:
{
  "user_id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "user_id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_admin": false,
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**POST /api/auth/forgot-password**
```json
Request:
{
  "email": "user@example.com"
}

Response:
{
  "message": "If an account exists with that email, a reset link has been sent"
}
```

**POST /api/auth/reset-password**
```json
Request:
{
  "token": "reset_token_from_email",
  "new_password": "new_secure_password"
}

Response:
{
  "message": "Password reset successfully"
}
```

**POST /api/auth/change-password** (Requires auth)
```json
Request:
{
  "current_password": "current_password",
  "new_password": "new_password"
}

Response:
{
  "message": "Password changed successfully"
}
```

**GET /api/auth/me** (Requires auth)
```json
Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_admin": false,
  "email_verified": true,
  "created_at": "2024-01-15T10:30:00"
}
```

#### User Profile Endpoints

**GET /api/users/profile** (Requires auth)
```json
Response:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_admin": false,
  "email_verified": true,
  "last_login": "2024-09-18T15:30:00",
  "created_at": "2024-01-15T10:30:00",
  "preferences": {...}
}
```

**PUT /api/users/profile** (Requires auth)
```json
Request:
{
  "full_name": "John Doe Updated",
  "email": "newemail@example.com",
  "language": "en",
  "timezone": "UTC"
}

Response:
{
  "id": "uuid",
  "email": "newemail@example.com",
  "username": "johndoe",
  "full_name": "John Doe Updated"
}
```

#### Preferences Endpoints

**GET /api/users/preferences** (Requires auth)
```json
Response:
{
  "id": "uuid",
  "email_notifications": {
    "workflow_started": true,
    "workflow_completed": true,
    "workflow_failed": true,
    "weekly_digest": true,
    "product_updates": false
  },
  "notification_frequency": "immediate",
  "theme": "system",
  "language": "en",
  "timezone": "UTC",
  "marketing_emails": false,
  "analytics_enabled": true
}
```

**PUT /api/users/preferences** (Requires auth)
```json
Request:
{
  "notification_frequency": "daily",
  "theme": "dark",
  "language": "es",
  "marketing_emails": true
}

Response:
{
  "message": "Preferences updated successfully"
}
```

#### API Keys Endpoints

**GET /api/users/api-keys** (Requires auth)
```json
Response:
{
  "api_keys": [
    {
      "id": "uuid",
      "name": "Production Key",
      "permissions": ["read", "write"],
      "last_used": "2024-09-18T15:30:00",
      "is_active": true,
      "created_at": "2024-09-10T10:00:00"
    }
  ]
}
```

**POST /api/users/api-keys** (Requires auth)
```json
Request:
{
  "name": "New API Key",
  "permissions": ["read", "write", "delete"]
}

Response:
{
  "id": "uuid",
  "name": "New API Key",
  "key": "sk_live_abc123...",
  "permissions": ["read", "write", "delete"],
  "created_at": "2024-09-18T15:30:00"
}
```

**DELETE /api/users/api-keys/{key_id}** (Requires auth)
```json
Response:
{
  "message": "API key deleted successfully"
}
```

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env`:
```
# Secret key (generate a secure one)
SECRET_KEY=your-secure-random-key

# Email Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Use App Password, not regular password
SENDER_NAME=Academian

# Frontend URLs
FRONTEND_URL=http://localhost:3000
PASSWORD_RESET_URL=http://localhost:3000/auth/reset-password

# Database
DATABASE_URL=sqlite:///./academian_platform.db

# Other settings
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Initialize Database

The database will be automatically initialized on server startup. Tables created:
- `users`
- `user_preferences`
- `api_keys`
- `user_sessions`
- `workflows`
- `workflow_executions`
- And more...

### 4. Run the Backend

```bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload
```

The API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

---

## 📧 Email Configuration

### Gmail Setup (Recommended for Development)

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App Passwords
   - Select Mail and Windows Computer (or similar)
   - Copy the generated 16-character password
3. Use this password in `.env` as `SENDER_PASSWORD`

### AWS SES Setup (Production)

```env
SMTP_SERVER=email-smtp.region.amazonaws.com
SMTP_PORT=587
SENDER_EMAIL=verified-email@yourdomain.com
SENDER_PASSWORD=your-smtp-password
```

### Custom SMTP Server

Update the `SMTP_SERVER` and `SMTP_PORT` in `.env` with your SMTP server details.

---

## 🔐 Security Features

### Implemented
✅ **Password Security**
- Bcrypt hashing with proper salt
- Password strength requirements
- Secure password reset token generation

✅ **Token Security**
- JWT with expiration (24 hours default)
- Secure token generation using secrets module
- Token hash verification (SHA256)

✅ **Email Security**
- Token expiration (24 hours for reset tokens)
- Secure random token generation
- HTTPS required for production

✅ **Database Security**
- Parameterized queries (SQLAlchemy ORM)
- SQL injection prevention
- Proper relationship management

### Recommended for Production
- [ ] Enable HTTPS only
- [ ] Implement rate limiting on auth endpoints
- [ ] Add CORS restrictions (don't use `allow_origins=["*"]`)
- [ ] Add request validation and sanitization
- [ ] Implement logging and monitoring
- [ ] Set strong `SECRET_KEY` (use `secrets.token_urlsafe(32)`)
- [ ] Enable database encryption
- [ ] Add account lockout after failed attempts
- [ ] Implement email verification for new accounts
- [ ] Add 2FA support

---

## 🧪 Testing

### Test User Registration
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePassword123!"
  }'
```

### Test User Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

### Test Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Password Reset
```bash
# Step 1: Request password reset
curl -X POST "http://localhost:8000/api/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Check email for reset link with token

# Step 2: Reset password with token
curl -X POST "http://localhost:8000/api/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "NewSecurePassword123!"
  }'
```

---

## 📊 Database Schema

### Users Table
- Stores user accounts with secure password hashing
- Tracks email verification and password reset tokens
- Records login activity

### User Preferences Table
- Notification settings
- Theme and language preferences
- Marketing and analytics preferences

### API Keys Table
- API key management
- Permissions control
- Usage tracking

### User Sessions Table
- Active session tracking
- Device information
- Last activity timestamp

---

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set critical variables
SECRET_KEY=<generated-secret>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=<app-password>
FRONTEND_URL=https://yourdomain.com
DEBUG=False
```

### Database Migration (PostgreSQL)

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@host:5432/academian

# Database tables will be created automatically on startup
```

---

## 🐛 Troubleshooting

### Email Not Sending
1. Check SMTP credentials in `.env`
2. Enable "Less secure app access" for Gmail (if applicable)
3. Check logs for SMTP errors
4. Verify firewall allows SMTP port (usually 587)

### Database Issues
1. Ensure write permissions in data directory
2. Check SQLite path is correct
3. For PostgreSQL, verify connection string
4. Run `init_db()` to create tables

### Token Validation Errors
1. Verify `SECRET_KEY` is set and consistent
2. Check token hasn't expired
3. Ensure JWT format: `Bearer <token>`
4. Verify ALGORITHM matches config

### CORS Issues
1. Verify frontend URL in CORS configuration
2. Check browser console for specific CORS errors
3. Ensure credentials are included in requests

---

## 📚 Files Modified/Created

```
backend/
├── app.py (Updated: +400 lines - new endpoints)
├── auth/
│   └── auth.py (Updated: +80 lines - new functions)
├── database/
│   └── models.py (Updated: +100 lines - new models)
├── services/
│   ├── __init__.py (Created)
│   └── email_service.py (Created: 250+ lines)
├── config.py (Updated: email settings)
├── requirements.txt (Updated: secure package)
├── .env.example (Updated: email config)
└── BACKEND_SETUP.md (This file)
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] SMTP credentials working
- [ ] Database initialized
- [ ] Server running (`http://localhost:8000`)
- [ ] Swagger docs accessible (`http://localhost:8000/docs`)
- [ ] Registration endpoint working
- [ ] Login endpoint working
- [ ] Password reset email sending
- [ ] User profile endpoints working
- [ ] API keys can be created

---

## 🔗 Integration with Frontend

The frontend already has all the necessary UI. Ensure:

1. Frontend `NEXT_PUBLIC_API_URL` points to backend:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. CORS is properly configured (currently allows all - restrict in production)

3. Token is stored in localStorage and sent in Authorization header:
   ```
   Authorization: Bearer <jwt_token>
   ```

---

## 📞 Support

For issues or questions:
1. Check the logs (`LOG_LEVEL=INFO` in config)
2. Review API documentation (`/docs`)
3. Verify `.env` configuration
4. Check database initialization

---

**Last Updated:** September 18, 2026
**Version:** 1.0.0
**Status:** Ready for Production (after security hardening)
