# Tujitume Backend API

FastAPI backend for the Tujitume Gig Platform.

## Features

- 🔐 Firebase Authentication
- 📝 Gig CRUD operations
- 💼 Application management
- 👤 User profiles
- 🔍 Advanced filtering and sorting
- 📊 PostgreSQL/SQLite database support
- 🚀 Auto-generated API documentation

## Tech Stack

- **Framework**: FastAPI 0.123.5
- **Database**: SQLAlchemy 2.0.44 (PostgreSQL/SQLite)
- **Authentication**: Firebase Admin SDK
- **Validation**: Pydantic 2.12.5
- **Server**: Uvicorn 0.38.0

## Project Structure

```
tujitume-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   └── models.py        # SQLAlchemy database models
│   ├── schemas/
│   │   └── schemas.py       # Pydantic validation schemas
│   ├── crud/
│   │   └── crud.py          # Database operations
│   ├── routers/
│   │   ├── gigs.py          # Gig endpoints
│   │   └── users.py         # User endpoints
│   ├── core/
│   │   └── dependencies.py  # Auth & DB dependencies
│   └── db/
│       └── database.py      # Database configuration
├── requirements.txt
├── .env
└── README.md
```

## Setup Instructions

### 1. Clone and Navigate

```bash
cd tujitume-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# For SQLite (development)
DATABASE_URL=sqlite:///./tujitume.db

# Or for PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/tujitume
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Gigs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/gigs` | List all gigs (with filters) | No |
| GET | `/api/gigs/{id}` | Get single gig | No |
| POST | `/api/gigs` | Create a gig | Yes |
| PUT | `/api/gigs/{id}` | Update a gig | Yes (Owner) |
| DELETE | `/api/gigs/{id}` | Delete a gig | Yes (Owner) |
| POST | `/api/gigs/{id}/apply` | Apply to a gig | Yes |
| GET | `/api/gigs/{id}/applications` | Get gig applications | Yes (Owner) |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me` | Get current user | Yes |
| GET | `/api/users/{uid}` | Get user by UID | No |
| GET | `/api/users/me/gigs` | Get my gigs | Yes |
| GET | `/api/users/me/applications` | Get my applications | Yes |

## Query Parameters (GET /api/gigs)

- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100, max: 100)
- `sort_by`: Field to sort by (`created_at` or `budget`)
- `sort_order`: Sort direction (`asc` or `desc`)
- `budget_type`: Filter by `fixed` or `hourly`
- `skills`: Comma-separated skills (e.g., `React,Python,AWS`)
- `search`: Search in title, description, or location

## Example API Calls

### List Gigs with Filters

```bash
curl "http://localhost:8000/api/gigs?budget_type=fixed&skills=React,Python&sort_by=budget&sort_order=desc"
```

### Get Single Gig

```bash
curl http://localhost:8000/api/gigs/1
```

### Create a Gig (Authenticated)

```bash
curl -X POST http://localhost:8000/api/gigs \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a React Dashboard",
    "description": "Looking for an experienced React developer...",
    "budget": 5000,
    "budget_type": "fixed",
    "location": "Remote",
    "skills_required": ["React", "TypeScript", "Tailwind"],
    "deadline": "2025-12-31T00:00:00Z"
  }'
```

### Apply to a Gig

```bash
curl -X POST http://localhost:8000/api/gigs/1/apply \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cover_letter": "I am an experienced developer with 5+ years..."
  }'
```

## Firebase Authentication

### Development Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file
6. Set the path in `.env`:
   ```
   FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
   ```

### Authentication Flow

1. Frontend authenticates user with Firebase
2. Frontend gets Firebase ID token
3. Frontend sends token in `Authorization: Bearer TOKEN` header
4. Backend verifies token with Firebase Admin SDK
5. Backend creates/retrieves user in database
6. Request proceeds with authenticated user context

## Database Models

### User
- `uid` (String, Primary Key) - Firebase UID
- `email` (String, Unique) - User email
- `name` (String) - Display name
- `created_at`, `updated_at` (DateTime)

### Gig
- `id` (Integer, Primary Key)
- `title` (String, Required)
- `description` (Text, Required)
- `budget` (Float)
- `budget_type` (String) - "fixed" or "hourly"
- `location` (String)
- `skills_required` (JSON Array)
- `deadline` (DateTime)
- `owner_id` (String, Foreign Key → User)
- `created_at`, `updated_at` (DateTime)

### Application
- `id` (Integer, Primary Key)
- `gig_id` (Integer, Foreign Key → Gig)
- `applicant_id` (String, Foreign Key → User)
- `cover_letter` (Text)
- `status` (String) - "pending", "accepted", "rejected"
- `created_at`, `updated_at` (DateTime)

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Database Migrations

For database migrations, consider using Alembic:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Deployment

### Using Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)

```env
DATABASE_URL=postgresql://user:password@db-host:5432/tujitume
FIREBASE_SERVICE_ACCOUNT_PATH=/app/secrets/serviceAccountKey.json
```

## Troubleshooting

### Database Connection Error

- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running (if using PostgreSQL)
- For SQLite, ensure write permissions in the directory

### Firebase Auth Not Working

- Verify `FIREBASE_SERVICE_ACCOUNT_PATH` is correct
- Check Firebase project configuration
- Ensure service account has necessary permissions

### CORS Issues

- Update `allow_origins` in `app/main.py` to include your frontend URL
- In production, never use `["*"]` for origins

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT
