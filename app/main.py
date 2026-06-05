from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes.intent import router as intent_router

load_dotenv()

app = FastAPI(
    title="TaskMeister API",
    description="AI-powered autonomous service procurement platform",
    version="0.1.0",
)

# Register routers
app.include_router(intent_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "TaskMeister API"}
