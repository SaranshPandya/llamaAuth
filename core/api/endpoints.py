from fastapi import FastAPI, HTTPException, status

import sys
sys.path.append("/Users/saranshpandya/gitprojects/inferproject/llamaAuth/")
from schemas.packet import RegisterUser, AuthenticateUserInput
from database_hander.databasehander import _db_manager
from core.encrypt.encryption import create_hash

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_app = FastAPI()


@_app.post("/users", status_code=201)
async def register_user(req: RegisterUser):
    try:
        passwordHash = await create_hash(string=req.password)
        user_id = _db_manager.register_user(
            username=req.username,
            passwordHash=passwordHash,
            email=req.email,
            age=req.age
        )
        
        return {"status": "success", "data": {"userId": user_id}}
    except Exception as e:
        logger.exception(f"Error occured while registering a user: {e}")
        return {"status": "failed", "response": "unable to register user."}
        # raise RuntimeError(f"Error occured while registering a user: {e}")

@_app.post("/authenticate_user")
async def authenticate_user(req: AuthenticateUserInput):
    try:
        passwordHash = await create_hash(string=req.password)
        users = _db_manager.authenticate_user(
            username=req.username, email=req.email
        )
        
        if not users:
            logger.debug(f"username or email {req.username if req.username else req.email} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            ) 
        
        if users[0].password != passwordHash:
            logger.debug(f"Incorrect password for {req.username if req.username else req.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Password"
            )
        
        logger.debug(f"username or email {req.username if req.username else req.email} authenticated")    
        return {"status": f"Welcome Back: {users[0].username}"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.exception(f"Error while authenticating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to authenticate"
            ) 