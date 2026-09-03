import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug_mode = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes"}
    
    display_host = "localhost" if host in {"127.0.0.1", "0.0.0.0"} else host
    print(f"Starting FastAPI backend on http://{display_host}:{port}  (debug={debug_mode})")
    print("Press Ctrl+C to stop.")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=debug_mode)
