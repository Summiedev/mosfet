from fastapi import APIRouter, HTTPException
from models import CreatePatient, PatientResponse
from database import users_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter(
    prefix= '/patients',
    tags=['Patient Worklist']
)

#CREATE A NEW PATIENT SCAN
@router.post('/',response_model=PatientResponse)
async def create_patient(patient: CreatePatient):
    new_patient = patient.dict()
    new_patient['created_at'] = datetime.utcnow()
    new_patient['status'] = 'pending'

    from database import patients_collection 
    result = await patients_collection.insert_one(new_patient)
    new_patient['id'] = str(result.inserted_id) 
    return new_patient

#GET ALL PATIENT SCANS(FOR THE DASHBOARD)
@router.get('/')
async def get_patients():
    from database import patients_collection 
    patients = []

#PATIENTS RECORD FOR MONGODB 
    async for patients in patients_collection.find():
       patients['id'] = str(patients['_id'])
       del patients ['_id']
       patients.append(patients)
       return patients