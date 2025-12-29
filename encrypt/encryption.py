from hashlib import sha256
from typing import Hashable
import logging


logger = logging.getLogger(__name__)

async def create_hash(string: str) -> str:
        """Creates sha256 hash of a string"""
        encoded = string.encode()
        encrypt = sha256(string=encoded).hexdigest()
        
        return encrypt


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_hash(string="Saransh Pandya"))

