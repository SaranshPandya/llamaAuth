# AUTH SERVER
import uvicorn

from core.api.endpoints import _app

if __name__ == "__main__":
    uvicorn.run(
        app="main:_app",
        host='0.0.0.0',
        port=5000
    )
