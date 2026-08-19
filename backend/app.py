import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in {"1", "true", "yes"}
    
    display_host = "localhost" if host == "127.0.0.1" else host
    print(f"Starting FastAPI backend on http://{display_host}:{port}  (debug={debug_mode})")
    print("Press Ctrl+C to stop.")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=debug_mode)
