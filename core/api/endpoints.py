import httpx
from fastapi import FastAPI, HTTPException, status
from schemas.packet import RegisterUser, AuthenticateUserInput, Chat
from database_hander.databasehander import _db_manager
from core.encrypt.encryption import create_hash
from core.encrypt.api_key_generator import key_generator

import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_app = FastAPI()


@_app.post("/register")
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
        logger.exception(f"Error occured while registering a user: {traceback.print_exc(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user."
        )
        # raise RuntimeError(f"Error occured while registering a user: {e}")

@_app.post("/login")
async def login(req: AuthenticateUserInput, getAPI: bool = False):
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
        
        elif getAPI:
            return users
         
        logger.debug(f"username or email {req.username if req.username else req.email} authenticated")    
        return {"status": f"Welcome Back: {users[0].username}"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.exception(f"Error while authenticating user: {traceback.print_exc(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to authenticate"
            )
        
        
@_app.post("/get_api")
async def get_api(req: AuthenticateUserInput):
    try:
        users = await login(req=req, getAPI=True)
        api_key_hash, api_key = await key_generator()
        # api_key_hash = await create_hash(string=api_key)    
        
        add_api_db = _db_manager.update_api_key(api_key_hash=api_key_hash, id=users[0].id)
        
        if add_api_db:
            return {"status": "success", "message": "Kindly save this API key because you will not be able to see it again.", "api_key": api_key}
        
    except Exception as e:
        logger.exception(f"Error generating API key: {traceback.print_exc(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate API key."
        )

@_app.post("/chat")
async def chat(req: Chat):
    try:
        api_key_hash = await create_hash(string=req.api_key)
        authenticate_api = _db_manager.authenticateAPIKey(api_key_hash=api_key_hash)
        
        if not req.base_url:
            req.base_url = "http://localhost:11434"

        if not authenticate_api:
            logging.exception(f"User not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        if api_key_hash != authenticate_api[1]:
            logging.exception(f"Invalid API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(
                url=f"{req.base_url}/api/generate",
                json = {
                    "model": req.model,
                    "prompt": req.query,
                    "stream": req.stream
                },
                timeout=None
            )
            
        return {"model_response": chat_response.json()}
        
        
    except HTTPException:
        raise
            
    except Exception as e:
        logger.exception(f"Error while generating model response: {traceback.print_exc(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate model response"        
        )
