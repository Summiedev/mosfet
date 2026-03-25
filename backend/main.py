from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {'message':'Radflow backend is officially live'}