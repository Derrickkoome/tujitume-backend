# 🚀 Tujitume Backend - Deployment Guide

## Prerequisites
- Python 3.8+
- PostgreSQL database
- Firebase Admin SDK credentials

## Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Firebase Admin SDK
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# CORS
CORS_ORIGINS=https://your-frontend-domain.com

# Optional
SECRET_KEY=your-secret-key
```

## Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
alembic upgrade head
```

### 3. Start the Server

#### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production (with Gunicorn)
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Heroku Deployment

1. Create `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create tujitume-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set FIREBASE_PROJECT_ID=...
git push heroku dev:main
heroku run alembic upgrade head
```

## Railway Deployment

1. Connect your GitHub repo
2. Add environment variables in Railway dashboard
3. Railway will auto-deploy on push

## Health Check

- Endpoint: `GET /`
- Response: `{"message": "Tujitume API is running"}`

## API Documentation

Once deployed, visit:
- Swagger UI: `https://your-domain/docs`
- ReDoc: `https://your-domain/redoc`

## Database Migration Notes

After deploying, always run migrations:
```bash
alembic upgrade head
```

## Recent Updates (Dec 8, 2025)

✅ Added user profile fields (bio, skills, phone, location)
✅ Enhanced application/gig endpoints with detailed data
✅ Added profile update endpoint
✅ Migration: a1b2c3d4e5f6_add_user_profile_fields.py

## Support

For issues, check the main documentation or open an issue on GitHub.
