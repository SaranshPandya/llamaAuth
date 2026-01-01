import secrets
import logging

from encryption import create_hash


logger = logging.getLogger(__name__)

async def key_generator(prefix: str = 'sk', nbytes: int = 32) -> tuple[str, str]:
    """Generating API key and storing it in sha256"""
    logger.debug("Generating key")
    generate = secrets.token_urlsafe(nbytes=32)
    key = f"{prefix}_{generate}"
    encode_key = await create_hash(string=key)
    
    return encode_key, key

if __name__ == "__main__":
    import asyncio

    asyncio.run(key_generator())             

