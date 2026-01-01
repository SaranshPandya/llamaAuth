from hashlib import sha256
from typing import Hashable
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(f"[{__file__, __name__}] ")

async def create_hash(string: str, hash_depth: int = 5) -> str:
        """Creates SHA256 hash of string with iterative hashing."""
        try:
                current_encrypt = string

                logger.debug("Generating SHA256 Hash...")
                for _ in range(hash_depth):
                        encoded = current_encrypt.encode()
                        encrypt = sha256(string=encoded).hexdigest()
                        current_encrypt = encrypt
                        
                print(encrypt)
                return encrypt

        except Exception as e:
                logging.exception(f"Unable to generate hash: {e}")
                raise RuntimeError(e)

if __name__ == "__main__":
        import asyncio
        
        asyncio.run(create_hash(string="saransh pandya"))
