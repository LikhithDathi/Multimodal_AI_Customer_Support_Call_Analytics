import uvicorn
import os
from app.config import Config

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=Config.DEBUG,
        workers=4 if not Config.DEBUG else 1
    )