# Educational Document Processing PoC

A proof of concept demonstrating a tenant isolated pipeline that converts uploaded educational documents into structured five slide presentations. The focus is on data layer tenant isolation and asynchronous processing.

## Tech Stack

- Backend: FastAPI, Python 3.12, SQLite via aiosqlite, Pydantic v2
- LLM: Llama via HuggingFace Inference Router using the OpenAI async client
- Auth: JWT via python jose and bcrypt
- Frontend: React 19, TypeScript 5, Vite 6, Tailwind CSS with DaisyUI theme dim

## Quick Start Backend

1. Navigate to the backend directory
2. Install dependencies with pip install requirements.txt
3. Create a .env file from .env.example and add your HuggingFace token
4. Run the server with uvicorn src.main:app reload
   The application automatically creates the database and seeds demo data for Alice and Bob tenants on first startup.

## API Endpoints

- GET health returns health status
- POST api/v1/auth/login returns a JWT token
- POST api/v1/documents/upload accepts PDF or TXT files under five megabytes
- POST api/v1/jobs queues a document for processing
- GET api/v1/jobs/job_id polls processing status
- GET api/v1/presentations/job_id retrieves the generated slides

## Validation Checklist

1. Log in with alice@eduorg.com and password demo1234
2. Upload a document and queue a job
3. Poll the job status until it completes
4. Fetch the presentation to verify the five structured slides
5. Critical isolation test: use the Alice token to request the Bob job. The response must be a 404 error

## Tenant Isolation

Every database query includes a tenant filter. The identifier is extracted exclusively from the JWT. Cross tenant access is blocked at the repository layer.

## Project Structure

- backend/src/config contains settings and environment variables
- backend/src/models contains Pydantic schemas
- backend/src/repositories contains raw SQL queries
- backend/src/services contains business logic and async workers
- backend/src/controllers contains FastAPI routers
- backend/src/middlewares contains authentication and error handling

## Note

This is a proof of concept. User registration, persistent sessions, and cloud storage are excluded to maintain architectural simplicity.

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
