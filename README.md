# Educational Document Processing PoC

A proof of concept demonstrating a tenant isolated pipeline that converts uploaded educational documents into structured five slide presentations using AI (Llama 3.1). The focus is on data layer tenant isolation, asynchronous processing, and intelligent content transformation.

## Live Demo

This PoC is deployed and publicly accessible for testing:

| Component         | URL                                                           | Status |
| ----------------- | ------------------------------------------------------------- | ------ |
| Frontend          | https://educational-document-processing-poc.vercel.app/       | Active |
| Backend API       | https://educational-document-processing-poc.onrender.com      | Active |
| API Documentation | https://educational-document-processing-poc.onrender.com/docs | Active |

### Quick Test Credentials

Use these accounts to test tenant isolation:

**Alice (Educational Organization)**

- Email: `alice@eduorg.com`
- Password: `demo1234`

**Bob (Training Company)**

- Email: `bob@trainco.com`
- Password: `demo5678`

### Testing Workflow

1. Access the frontend: https://educational-document-processing-poc.vercel.app/
2. Login with Alice credentials
3. Upload a document or use one from the `sample_data/` folder
4. Click "Process" and wait ~15-30 seconds for AI generation
5. Click "View" to see the structured presentation
6. Logout and login as Bob to verify tenant isolation

### Important Notes

- The backend uses SQLite on Render free tier. All data (users, documents, uploads) is volatile and will be lost on redeploy or after ~15 minutes of inactivity.
- The first request after inactivity may take 30-60 seconds due to cold start on Render free tier.
- For persistent storage and production use, configure PostgreSQL and cloud storage as described in the "Notes" section.

### API Access

Direct API calls can be made to the backend:

````bash
# Health check
curl https://educational-document-processing-poc.onrender.com/health

# Login
curl -X POST https://educational-document-processing-poc.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@eduorg.com","password":"demo1234"}'

# List documents (requires JWT from login)
curl https://educational-document-processing-poc.onrender.com/api/v1/documents/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

## Quick Start

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from example
cp .env.example .env
# Edit .env and add your HuggingFace API token:
# HF_API_TOKEN=your_token_here

# 5. Run the server
uvicorn src.main:app --reload
````

Backend runs on: http://localhost:8000  
API Docs: http://localhost:8000/docs

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# 4. Run the development server
npm run dev
```

Frontend runs on: http://localhost:3000

## Sample Test Data

The `sample_data/` folder contains two pre prepared test documents:

1. `machine_learning_intro.txt` - Introduction to Neural Networks and Deep Learning  
   Dense technical content about ANN architectures, training, and applications

2. `distributed_systems_raw.txt` - Distributed Systems Fundamentals  
   Complex concepts covering CAP theorem, consensus algorithms, and observability

These files are intentionally unformatted to test the AI ability to extract structure and create pedagogical slides.

## Test User Credentials

### User 1: Alice (Educational Organization)

- Email: `alice@eduorg.com`
- Password: `demo1234`
- Tenant ID: `t-alpha-0001-0000-0000-000000000001`
- Pre loaded documents: 2 (Photosynthesis, Cell Division)

### User 2: Bob (Training Company)

- Email: `bob@trainco.com`
- Password: `demo5678`
- Tenant ID: `t-beta-0002-0000-0000-000000000002`
- Pre loaded documents: 1 (Workplace Safety)

## Workflow

1. Login with Alice or Bob credentials
2. Upload a document (PDF or TXT, max 5MB) or use sample data
3. Click "Process" to queue the document for AI transformation
4. Wait ~10-20 seconds (auto refresh shows progress)
5. Click "View" to see the generated five slide presentation
6. Test isolation: Login as Bob and verify you cannot see Alice documents

## Tech Stack

| Layer    | Technology                                                               |
| -------- | ------------------------------------------------------------------------ |
| Backend  | FastAPI, Python 3.12, SQLite (aiosqlite), Pydantic v2                    |
| LLM      | Llama 3.1 8B via HuggingFace Inference Router (OpenAI compatible client) |
| Auth     | JWT (python-jose), bcrypt password hashing                               |
| Frontend | React 19, TypeScript 5, Vite 6, Tailwind CSS + DaisyUI (dim theme)       |
| Async    | asyncio background workers, polling for job status                       |

## API Endpoints

| Method | Endpoint                         | Description                                 |
| ------ | -------------------------------- | ------------------------------------------- |
| GET    | `/health`                        | Health check                                |
| POST   | `/api/v1/auth/login`             | Authenticate and receive JWT token          |
| POST   | `/api/v1/documents/upload`       | Upload PDF/TXT (max 5MB)                    |
| GET    | `/api/v1/documents/`             | List all documents for authenticated tenant |
| POST   | `/api/v1/jobs/`                  | Queue a document for processing             |
| GET    | `/api/v1/jobs/{job_id}`          | Poll job processing status                  |
| GET    | `/api/v1/presentations/{job_id}` | Retrieve generated five slide presentation  |

## Validation Checklist

- [ ] Login with `alice@eduorg.com` / `demo1234`
- [ ] Upload `sample_data/machine_learning_intro.txt`
- [ ] Click "Process" and watch status change: `uploaded` -> `processing` -> `completed`
- [ ] Click "View" to verify five structured slides were generated
- [ ] Critical Test: Logout, login as Bob, verify Alice documents are NOT visible
- [ ] Security Test: Try accessing `/api/v1/documents/` with Bob token to fetch Alice doc -> must return `404`

## Tenant Isolation

- Every database query includes a `WHERE tenant_id = :tenant_id` filter
- Tenant ID is extracted exclusively from the JWT token (never from request body)
- Cross tenant access is blocked at the repository layer (SQL enforcement)
- File storage is physically separated: `storage/{tenant_id}/{document_id}/`

## Project Structure

```
backend/src/
├── config/           # Settings and environment variables
├── models/           # Pydantic schemas (request/response)
├── repositories/     # Raw SQL queries with tenant isolation
├── services/         # Business logic and async workers
├── routes/           # FastAPI routers (controllers)
└── middlewares/      # JWT authentication and error handling

frontend/src/
├── pages/            # Dashboard, JobDetail, LoginPage
├── components/       # Reusable UI components
├── hooks/            # useAuth for JWT management
└── lib/              # API client with axios interceptors
```

## Notes

This is a proof of concept. The following features are intentionally excluded to maintain architectural simplicity:

- User registration (users are seeded on first startup)
- Persistent sessions (JWT only, no refresh tokens)
- Cloud storage (local filesystem only)
- Email verification or password recovery
- Rate limiting or advanced security headers

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
