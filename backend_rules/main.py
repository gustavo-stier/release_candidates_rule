from fastapi import FastAPI

app = FastAPI()

from auth_routes import auth_router  # noqa: E402
from rules_routes import rules_router  # noqa: E402

# uvicorn main:app --reload

app.include_router(auth_router)
app.include_router(rules_router)
