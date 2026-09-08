import sys
import os
from pathlib import Path

# Force execution using the dedicated virtual environment
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent

venv_candidates = [
    backend_dir / "venv" / "Scripts" / "python.exe",
    project_root / ".venv" / "Scripts" / "python.exe",
    project_root / "venv" / "Scripts" / "python.exe",
]
venv_python = next((p for p in venv_candidates if p.exists()), None)

if venv_python and Path(sys.executable).resolve() != venv_python.resolve():
    import subprocess
    sys.exit(subprocess.call([str(venv_python)] + sys.argv, cwd=str(backend_dir)))

import uvicorn
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug_mode = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes"}
    
    display_host = "localhost" if host in {"127.0.0.1", "0.0.0.0"} else host
    print(f"Starting FastAPI backend on http://{display_host}:{port}  (debug={debug_mode})")
    print("Press Ctrl+C to stop.")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=debug_mode)
