"""
Utility to start/stop/restart a uvicorn subprocess for the generated FastAPI app.

Strategy:
- We shell out to `uvicorn generated_fastapi_app:app --port <port>`
- When regenerating, we terminate old proc and start a new one.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path
from typing import Optional
from security import safe_command

class APIServerRunner:
    def __init__(self, app_module_path: Path, port: int = 8001):
        self.app_module_path = Path(app_module_path)
        self.port = port
        self._proc: Optional[subprocess.Popen] = None

    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def start(self):
        if self.is_running():
            return
        self._proc = self._spawn()

    def stop(self):
        if not self.is_running():
            return
        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        self._proc = None

    def restart(self):
        self.stop()
        # Slight delay to release port
        time.sleep(0.5)
        self.start()

    def _spawn(self) -> subprocess.Popen:
        """
        Launch uvicorn in a subprocess. We use `python -m uvicorn` so we inherit env.
        We must specify the full module path: use file path with colon.
        """
        # Use module name relative to the parent directory
        module_name = self.app_module_path.stem
        target = f"{module_name}:app"
        
        cmd = [sys.executable, "-m", "uvicorn", target, "--host", "0.0.0.0", "--port", str(self.port)]
        
        # Change to the directory containing the generated app
        cwd = str(self.app_module_path.parent)
        
        env = os.environ.copy()
        # Ensure Python can import the generated file
        env["PYTHONPATH"] = cwd + os.pathsep + env.get("PYTHONPATH", "")
        
        return safe_command.run(subprocess.Popen, cmd, env=env, cwd=cwd)
