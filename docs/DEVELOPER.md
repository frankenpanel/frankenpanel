# Developer Guide

## Development Setup

### Backend Development

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd FrankenPanel
   ```

2. **Setup Python Environment**
   ```bash
   cd backend
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize Database**
   ```bash
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core utilities
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # FastAPI app
├── requirements.txt
└── .env

frontend/
├── src/
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── contexts/     # React contexts
│   ├── hooks/        # Custom hooks
│   ├── services/     # API services
│   └── App.tsx
├── package.json
└── vite.config.ts
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting
- Use isort for imports

### TypeScript/React
- Use TypeScript strict mode
- Functional components with hooks
- Use ESLint and Prettier
- Follow React best practices

## Testing

### Backend Tests
```bash
pytest tests/
```

### Frontend Tests
```bash
npm test
```

## Database Migrations

Use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Development

1. Define Pydantic schemas in `app/schemas/`
2. Create database models in `app/models/`
3. Implement business logic in `app/services/`
4. Create API routes in `app/api/v1/`
5. Add authentication and permission checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Debugging

### Backend
- Use `print()` or logging for debugging
- Check FastAPI docs at `/docs`
- Review database queries in logs

### Frontend
- Use React DevTools
- Check browser console
- Use network tab for API calls
