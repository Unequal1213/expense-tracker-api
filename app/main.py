from fastapi import FastAPI

from app.api.categories import router as categories_router

app = FastAPI(
    title="Expense Tracker API",
    version="0.1.0",
)

app.include_router(categories_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
