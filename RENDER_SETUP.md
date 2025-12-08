# Render Deployment Configuration

## Important: In Render Dashboard

### 1. Set Environment Variables

Go to your service → Environment tab and add:

```
DATABASE_URL=<your-postgres-connection-string>
FIREBASE_PROJECT_ID=tujitume-frontend-4fbbf
FIREBASE_PRIVATE_KEY_ID=<from-firebase-service-account>
FIREBASE_PRIVATE_KEY=<from-firebase-service-account>
FIREBASE_CLIENT_EMAIL=<from-firebase-service-account>
FIREBASE_CLIENT_ID=<from-firebase-service-account>
FIREBASE_CLIENT_CERT_URL=<from-firebase-service-account>
CORS_ORIGINS=https://tujitume-app.netlify.app,http://localhost:5173
```

### 2. Set Build & Start Commands

In Render Dashboard → Settings → Build & Deploy:

**Build Command:**
```
pip install -r requirements.txt && alembic upgrade head
```

**Start Command:**
```
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### 3. Deploy Settings

- **Environment**: Python 3
- **Python Version**: 3.12.0 (via PYTHON_VERSION env var)
- **Branch**: main
- **Auto-Deploy**: Yes

## Why gunicorn?

Gunicorn is a production WSGI server that:
- Manages multiple worker processes
- Handles graceful restarts
- Better for production than `uvicorn` alone
- Uses `uvicorn.workers.UvicornWorker` for async support

## Troubleshooting

### If deployment still fails:

1. Check the start command is exactly:
   ```
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

2. Verify gunicorn is in requirements.txt

3. Check logs for database connection issues

4. Make sure all environment variables are set
