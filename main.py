from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import routerimportMcdo

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Import fascicules Mcdo",
    description="API pour lire des pdfs et mettre à jour des fichiers Excel",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["https://dev.azert.fr/"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du router
app.include_router(routerimportMcdo, prefix="/Import-Fascicules-Mcdo", tags=["Import fascicules Mcdo"])