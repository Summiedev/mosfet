from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# USER AUTHENTICATION SCHEMAS
class CreateUser(BaseModel):   #FOR STAFF LOGIN
    username : str
    email : EmailStr
    password : int
   
class UserResponse(BaseModel):
    id : str
    username : str
    email : EmailStr
    email : EmailStr
   
class CreatePatient(BaseModel):    #patient login
     username : str
     age : int
     gender : str
     scan_type : str   #e.g ultrasound
     reason : str #The reason for doing the scan

class PatientResponse(CreatePatient):
    id : int
    time_created : datetime
    status : str 
