from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import level_fa, PatientProgram, CreadCard

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(level_fa.router, prefix="/api")
app.include_router(PatientProgram.router, prefix="/api")
app.include_router(CreadCard.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "MoleScane Rehabilitation API"}