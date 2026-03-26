from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# USER AUTHENTICATION SCHEMAS
class CreateUser(BaseModel):   #FOR STAFF LOGIN
    username : str
    email : EmailStr
    password : str
   
class UserResponse(BaseModel):
    id : str
    username : str
    email : EmailStr
    
   
class CreatePatient(BaseModel):    #patient login
     username : str
     age : int
     gender : str
     scan_type : str   #e.g ultrasound
     reason : str #The reason for doing the scan

class PatientResponse(CreatePatient):
    id : str
    time_created : datetime
    status : str 

class ChecklistItem(BaseModel):  #SCAN SESSION SCHEMA
    item_description: str
    is_checked: bool = False

class ChecklistUpdate(BaseModel):
    is_checked: bool = False

class ScanSessionCreate(BaseModel):
    patient_id : str
    scan_type : str        #EXAMPLE -> XRAY, CT SCAN

class UpdateTranscript(BaseModel):
    text:str    #voice to text

class ScanSessionResponse(BaseModel):
    patient_id : str
    scan_type : str
    id : str
    status : str = 'in progress'
    transcript : list[str] = []
    checklist : list[ChecklistItem] = []
    time_created : datetime

class ReportUpdate(BaseModel):
    findings : str
    status : str    