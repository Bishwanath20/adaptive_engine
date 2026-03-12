from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import session, questions
from app.core.database import connect_db, disconnect_db

app = FastAPI(
    title="Adaptive Diagnostic Engine",
    description="1D Adaptive Testing System with IRT-based ability estimation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/api", tags=["Session"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])


@app.on_event("startup")
async def startup():
    await connect_db()


@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()


@app.get("/")
async def root():
    return {"message": "Adaptive Diagnostic Engine is running 🚀"}
