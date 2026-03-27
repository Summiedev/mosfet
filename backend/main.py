from fastapi import FastAPI
from auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

@app.get('/home')
def home():
    return {'message':'Radflow backend is officially live'}