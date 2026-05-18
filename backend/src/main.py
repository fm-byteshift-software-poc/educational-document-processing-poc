import json
import os
import bcrypt
import aiofiles
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.repositories.database import init_db, get_db
from src.repositories import create_tenant, create_document, create_job, create_presentation
from src.routes import api_router
from src.middlewares.error_handler import register_exception_handlers


async def _seed_database() -> None:
    """Inserts deterministic seed data if the database is initially empty."""
    await create_tenant({
        "id": "t-alpha-0001-0000-0000-000000000001",
        "email": "alice@eduorg.com",
        "password_hash": bcrypt.hashpw("demo1234".encode(), bcrypt.gensalt(rounds=12)).decode(),
        "created_at": "2026-05-01T10:00:00Z"
    })
    await create_tenant({
        "id": "t-beta-0002-0000-0000-000000000002",
        "email": "bob@trainco.com",
        "password_hash": bcrypt.hashpw("demo5678".encode(), bcrypt.gensalt(rounds=12)).decode(),
        "created_at": "2026-05-01T10:05:00Z"
    })

    seed_docs = [
        {
            "id": "doc-alpha-001", "tenant_id": "t-alpha-0001-0000-0000-000000000001",
            "filename": "intro_to_photosynthesis.txt", "status": "completed",
            "uploaded_at": "2026-05-10T09:00:00Z",
            "content": "Photosynthesis is the biological process by which green plants, algae, and some bacteria convert light energy, usually from the sun, into chemical energy stored in glucose. This process takes place primarily in the chloroplasts, organelles found in plant cells that contain the green pigment chlorophyll. Chlorophyll absorbs light most efficiently in the blue and red wavelengths while reflecting green light, which is why plants appear green to the human eye.\n\nThe overall chemical equation for photosynthesis is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. The process is divided into two main stages: the light-dependent reactions, which occur in the thylakoid membranes and capture energy from sunlight to produce ATP and NADPH, and the light-independent reactions (Calvin cycle), which take place in the stroma and use that energy to fix carbon dioxide into organic molecules.\n\nPhotosynthesis is fundamental to life on Earth because it produces oxygen as a byproduct and forms the base of almost all food chains. Factors such as light intensity, carbon dioxide concentration, temperature, and water availability directly affect the rate of photosynthesis. Understanding this process has practical applications in agriculture, biofuel production, and climate science."
        },
        {
            "id": "doc-alpha-002", "tenant_id": "t-alpha-0001-0000-0000-000000000001",
            "filename": "cell_division_basics.txt", "status": "uploaded",
            "uploaded_at": "2026-05-11T11:30:00Z",
            "content": "Cell division is the process by which a parent cell divides into two or more daughter cells. It is a fundamental mechanism for growth, repair, and reproduction in all living organisms. In eukaryotic cells, the two main types of cell division are mitosis and meiosis, each serving distinct biological purposes.\n\nMitosis is a form of cell division that results in two genetically identical daughter cells, each with the same chromosome number as the parent cell. It proceeds through four main phases: prophase, metaphase, anaphase, and telophase, followed by cytokinesis. Mitosis is essential for growth and tissue repair in multicellular organisms.\n\nMeiosis, in contrast, produces four genetically distinct daughter cells with half the chromosome number of the parent cell. This process is critical for sexual reproduction as it generates gametes — sperm and egg cells. Errors in cell division can lead to conditions such as cancer, where cells divide uncontrollably, or chromosomal disorders caused by abnormal chromosome numbers."
        },
        {
            "id": "doc-beta-001", "tenant_id": "t-beta-0002-0000-0000-000000000002",
            "filename": "workplace_safety_module.txt", "status": "completed",
            "uploaded_at": "2026-05-12T14:00:00Z",
            "content": "Workplace safety refers to the policies, procedures, and practices designed to protect employees from accidents, injuries, and occupational illnesses. It is governed in many countries by regulatory bodies such as OSHA in the United States, which sets and enforces standards for safe and healthy working conditions.\n\nKey components of an effective workplace safety program include hazard identification and risk assessment, employee training and education, proper use of personal protective equipment (PPE), incident reporting and investigation procedures, and emergency response planning. Regular safety audits and drills help ensure that procedures remain effective and that employees are prepared.\n\nA strong safety culture requires commitment at all levels of an organization. Supervisors must model safe behavior and address unsafe conditions promptly. Employees should feel empowered to report hazards without fear of retaliation. Studies consistently show that organizations with proactive safety programs experience fewer incidents, lower insurance costs, higher employee morale, and greater overall productivity."
        }
    ]

    for doc in seed_docs:
        dir_path = os.path.join(settings.STORAGE_PATH, doc["tenant_id"], doc["id"])
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, doc["filename"])
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(doc["content"])

        await create_document({
            "id": doc["id"], "tenant_id": doc["tenant_id"], "filename": doc["filename"],
            "stored_path": file_path, "mime_type": "text/plain",
            "uploaded_at": doc["uploaded_at"], "status": doc["status"]
        })

    await create_job({
        "id": "job-alpha-001", "tenant_id": "t-alpha-0001-0000-0000-000000000001",
        "document_id": "doc-alpha-001", "created_at": "2026-05-10T09:01:00Z",
        "processing_status": "completed", "error_message": None
    })
    await create_job({
        "id": "job-beta-001", "tenant_id": "t-beta-0002-0000-0000-000000000002",
        "document_id": "doc-beta-001", "created_at": "2026-05-12T14:01:00Z",
        "processing_status": "completed", "error_message": None
    })

    slides_alpha = [
        {"slide_number": 1, "section": "Overview", "heading": "What Is Photosynthesis?", "body": "Photosynthesis is the process by which plants, algae, and certain bacteria convert light energy into chemical energy stored as glucose. It occurs primarily in chloroplasts, which contain the pigment chlorophyll responsible for absorbing sunlight. This process is foundational to nearly all life on Earth."},
        {"slide_number": 2, "section": "Key Concepts", "heading": "The Chemistry of Photosynthesis", "body": "The overall reaction is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. Photosynthesis is divided into light-dependent reactions in the thylakoid membranes and the Calvin cycle in the stroma. These two stages work together to capture energy and fix carbon dioxide into organic molecules."},
        {"slide_number": 3, "section": "Core Content", "heading": "Light-Dependent and Light-Independent Reactions", "body": "Light-dependent reactions capture solar energy to produce ATP and NADPH, releasing oxygen as a byproduct. The Calvin cycle uses this stored energy to convert carbon dioxide into glucose. Chlorophyll absorbs blue and red wavelengths most efficiently, reflecting green light and giving plants their characteristic color."},
        {"slide_number": 4, "section": "Practical Application", "heading": "Factors That Affect Photosynthesis", "body": "Light intensity, carbon dioxide concentration, temperature, and water availability all directly influence the rate of photosynthesis. Understanding these factors has practical implications for agricultural yield optimization and crop management. It also informs biofuel research and our understanding of carbon cycling in climate science."},
        {"slide_number": 5, "section": "Summary", "heading": "Why Photosynthesis Matters", "body": "Photosynthesis produces the oxygen that supports aerobic life and forms the energy base of almost all food chains. It represents the primary mechanism through which solar energy enters biological systems. Continued research into photosynthesis drives advances in agriculture, renewable energy, and climate modeling."}
    ]

    slides_beta = [
        {"slide_number": 1, "section": "Overview", "heading": "What Is Workplace Safety?", "body": "Workplace safety encompasses the policies, procedures, and practices that protect employees from accidents, injuries, and occupational illnesses. Regulatory bodies such as OSHA establish and enforce the standards organizations must follow. A safe workplace is both a legal requirement and an operational priority."},
        {"slide_number": 2, "section": "Key Concepts", "heading": "Core Components of a Safety Program", "body": "Effective safety programs include hazard identification, employee training, proper use of personal protective equipment, incident reporting, and emergency response planning. Each component addresses a distinct risk category in the workplace. Together they create a layered defense against occupational harm."},
        {"slide_number": 3, "section": "Core Content", "heading": "Risk Assessment and Hazard Control", "body": "Hazard identification and risk assessment are the foundation of any safety program. Regular safety audits and emergency drills keep procedures current and employees prepared. Incident investigation after near-misses and accidents provides data that drives continuous improvement."},
        {"slide_number": 4, "section": "Practical Application", "heading": "Building a Safety Culture", "body": "Safety culture requires commitment at every organizational level, from executive leadership to frontline employees. Supervisors must model safe behavior and respond promptly to reported hazards. Employees must feel empowered to raise concerns without fear of retaliation."},
        {"slide_number": 5, "section": "Summary", "heading": "The Business Case for Safety", "body": "Organizations with proactive safety programs consistently report fewer workplace incidents, lower insurance and liability costs, and higher employee morale. Safety investment directly correlates with productivity and retention. A structured, auditable safety program is also a competitive differentiator for institutional clients."}
    ]

    await create_presentation({
        "id": "pres-alpha-001", "tenant_id": "t-alpha-0001-0000-0000-000000000001",
        "job_id": "job-alpha-001", "source_document_id": "doc-alpha-001",
        "presentation_version": 1, "title": "Introduction to Photosynthesis",
        "slides": json.dumps(slides_alpha), "generated_at": "2026-05-10T09:02:00Z"
    })
    await create_presentation({
        "id": "pres-beta-001", "tenant_id": "t-beta-0002-0000-0000-000000000002",
        "job_id": "job-beta-001", "source_document_id": "doc-beta-001",
        "presentation_version": 1, "title": "Workplace Safety Module",
        "slides": json.dumps(slides_beta), "generated_at": "2026-05-12T14:02:00Z"
    })


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifecycle manager: initializes DB, runs seed if empty, yields control."""
    await init_db(settings.DATABASE_URL)

    async with get_db() as db:
        cursor = await db.execute("SELECT COUNT(*) FROM tenants")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await _seed_database()

    yield


app = FastAPI(lifespan=lifespan, title="Educational Document Processing PoC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)