from hashlib import sha256
from typing import Hashable
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(f"{__name__} ")

async def create_hash(string: str) -> str:
        try:
                """Creates sha256 hash of a string"""
                logger.debug("Generating SHA256 hash")
                encoded = string.encode()
                encrypt = sha256(string=encoded).hexdigest()

                return encrypt

        except Exception as e:
                logging.exception(f"Unable to generate hash: {e}")
                raise RuntimeError(e)

if __name__ == "__main__":
    import asyncio

    asyncio.run(create_hash(string="Saransh Pandya"))
