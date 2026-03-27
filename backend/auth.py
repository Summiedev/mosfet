from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from models import CreateUser
from database import users_collection

router = APIRouter(
    prefix = '/auth',
    tags= ['Authentication']
)

#encrypting the password
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

@router.post('/signup')
async def signup(user : CreateUser):
    existing_user = await users_collection.find_one({'email':user.email})
    if existing_user :
        raise HTTPException(status_code=400, details = 'Email already exists')
        
    #encrypt password
    hashed_password = pwd_context.hash(user.password) 

    new_user = {
    'username': user.username,
    'email': user.email,
    'password': hashed_password
    }
        

    result = await users_collection.insert_one(new_user)
    return {
    'message': 'USER SUCCESSFULLY CREATED!!',
    'user_id': str(result.inserted_id)
    }