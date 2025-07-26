"""
API Server Runner
================

Manages the lifecycle of the generated FastAPI server.
Handles starting, stopping, and restarting the API server process.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIServerRunner:
    """
    Manages the lifecycle of a FastAPI server process.
    
    Handles starting, stopping, and restarting the server with proper
    process management and error handling.
    """
    
    def __init__(self, app_module_path: Path, port: int = 8001, host: str = "0.0.0.0"):
        """
        Initialize the API server runner.
        
        Args:
            app_module_path: Path to the generated FastAPI app file
            port: Port to run the server on
            host: Host to bind the server to
        """
        self.app_module_path = Path(app_module_path)
        self.port = port
        self.host = host
        self._process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
        
        # Validate app path
        if not self.app_module_path.exists():
            logger.warning(f"App file does not exist: {self.app_module_path}")
    
    def is_running(self) -> bool:
        """
        Check if the server process is currently running.
        
        Returns:
            True if the server is running, False otherwise
        """
        if self._process is None:
            return False
        
        # Check if process is still alive
        return self._process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed status information about the server.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            "running": self.is_running(),
            "port": self.port,
            "host": self.host,
            "app_path": str(self.app_module_path),
            "app_exists": self.app_module_path.exists(),
            "uptime": None,
            "pid": None
        }
        
        if self.is_running():
            status["pid"] = self._process.pid
            if self._start_time:
                status["uptime"] = time.time() - self._start_time
        
        return status
    
    def start(self, timeout: int = 10) -> bool:
        """
        Start the API server process.
        
        Args:
            timeout: Maximum time to wait for server to start (seconds)
            
        Returns:
            True if server started successfully, False otherwise
        """
        if self.is_running():
            logger.info("Server is already running")
            return True
        
        if not self.app_module_path.exists():
            logger.error(f"Cannot start server: app file not found at {self.app_module_path}")
            return False
        
        try:
            # Build command
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                f"{self.app_module_path.stem}:app",
                "--host", self.host,
                "--port", str(self.port),
                "--reload"
            ]
            
            # Set environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.app_module_path.parent) + os.pathsep + env.get("PYTHONPATH", "")
            
            # Start process
            logger.info(f"Starting API server on {self.host}:{self.port}")
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self.app_module_path.parent),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self._start_time = time.time()
            
            # Wait for server to start
            if self._wait_for_server(timeout):
                logger.info(f"API server started successfully (PID: {self._process.pid})")
                return True
            else:
                logger.error("Server failed to start within timeout")
                self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self, timeout: int = 5) -> bool:
        """
        Stop the API server process.
        
        Args:
            timeout: Maximum time to wait for graceful shutdown (seconds)
            
        Returns:
            True if server stopped successfully, False otherwise
        """
        if not self.is_running():
            logger.info("Server is not running")
            return True
        
        try:
            logger.info(f"Stopping API server (PID: {self._process.pid})")
            
            # Try graceful shutdown first
            self._process.terminate()
            
            # Wait for graceful shutdown
            try:
                self._process.wait(timeout=timeout)
                logger.info("Server stopped gracefully")
                return True
            except subprocess.TimeoutExpired:
                logger.warning("Graceful shutdown timeout, forcing kill")
                
                # Force kill
                self._process.kill()
                try:
                    self._process.wait(timeout=2)
                    logger.info("Server force-killed")
                    return True
                except subprocess.TimeoutExpired:
                    logger.error("Failed to kill server process")
                    return False
                    
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return False
        finally:
            self._process = None
            self._start_time = None
    
    def restart(self, timeout: int = 10) -> bool:
        """
        Restart the API server process.
        
        Args:
            timeout: Maximum time to wait for server to restart (seconds)
            
        Returns:
            True if server restarted successfully, False otherwise
        """
        logger.info("Restarting API server")
        
        # Stop current server
        if not self.stop():
            logger.warning("Failed to stop existing server, attempting restart anyway")
        
        # Small delay to ensure port is released
        time.sleep(0.5)
        
        # Start new server
        return self.start(timeout)
    
    def _wait_for_server(self, timeout: int) -> bool:
        """
        Wait for the server to be ready to accept connections.
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if server is ready, False if timeout
        """
        import socket
        import requests
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if process is still running
            if not self.is_running():
                return False
            
            # Try to connect to the server
            try:
                # Check if port is open
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                sock.close()
                
                if result == 0:
                    # Try HTTP request
                    try:
                        response = requests.get(f"http://{self.host}:{self.port}/docs", timeout=2)
                        if response.status_code == 200:
                            return True
                    except requests.RequestException:
                        pass
                        
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def get_logs(self, lines: int = 50) -> str:
        """
        Get recent server logs.
        
        Args:
            lines: Number of lines to retrieve
            
        Returns:
            Recent log output as string
        """
        if not self.is_running() or self._process is None:
            return "Server is not running"
        
        try:
            # This is a simplified version - in practice, you might want to
            # implement a more sophisticated log collection mechanism
            return f"Server running (PID: {self._process.pid}) - logs not available in this implementation"
        except Exception as e:
            return f"Error retrieving logs: {e}"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the server.
        
        Returns:
            Health check results
        """
        import requests
        
        health_info = {
            "status": "unknown",
            "response_time": None,
            "endpoints": [],
            "error": None
        }
        
        if not self.is_running():
            health_info["status"] = "stopped"
            return health_info
        
        try:
            # Check main endpoint
            start_time = time.time()
            response = requests.get(f"http://{self.host}:{self.port}/docs", timeout=5)
            response_time = time.time() - start_time
            
            health_info["response_time"] = response_time
            
            if response.status_code == 200:
                health_info["status"] = "healthy"
                
                # Try to get available endpoints
                try:
                    openapi_response = requests.get(f"http://{self.host}:{self.port}/openapi.json", timeout=2)
                    if openapi_response.status_code == 200:
                        spec = openapi_response.json()
                        health_info["endpoints"] = list(spec.get("paths", {}).keys())
                except Exception:
                    pass
            else:
                health_info["status"] = "unhealthy"
                health_info["error"] = f"HTTP {response.status_code}"
                
        except requests.RequestException as e:
            health_info["status"] = "unreachable"
            health_info["error"] = str(e)
        except Exception as e:
            health_info["status"] = "error"
            health_info["error"] = str(e)
        
        return health_info
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def create_server_runner(app_path: str, port: int = 8001, host: str = "0.0.0.0") -> APIServerRunner:
    """
    Create a new API server runner instance.
    
    Args:
        app_path: Path to the FastAPI app file
        port: Port to run the server on
        host: Host to bind the server to
        
    Returns:
        Configured APIServerRunner instance
    """
    return APIServerRunner(
        app_module_path=Path(app_path),
        port=port,
        host=host
    )


def check_port_available(host: str, port: int) -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        host: Host to check
        port: Port to check
        
    Returns:
        True if port is available, False otherwise
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False


def find_available_port(host: str, start_port: int = 8001, max_attempts: int = 100) -> Optional[int]:
    """
    Find an available port starting from the given port.
    
    Args:
        host: Host to check
        start_port: Starting port number
        max_attempts: Maximum number of ports to check
        
    Returns:
        Available port number or None if none found
    """
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(host, port):
            return port
    return None 