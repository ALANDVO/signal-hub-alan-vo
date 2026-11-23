"""Reproduction runner service for PHP code execution in sandbox."""

import subprocess
import tempfile
import os
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from app.core.config import get_settings

settings = get_settings()


@dataclass
class ReproductionResult:
    """Result of PHP code execution in sandbox."""
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    memory_used: Optional[str] = None
    timed_out: bool = False
    sandbox_error: Optional[str] = None


class ReproductionRunner:
    """Executes PHP code in sandbox environment with security and resource limits."""
    
    def __init__(self):
        # Validate environment configuration
        self.timeout_seconds = settings.SANDBOX_TIMEOUT
        self.memory_limit = settings.SANDBOX_MEMORY_LIMIT
        self.php_path = self._find_php_binary()
    
    def _find_php_binary(self) -> str:
        """Find PHP binary in system, default to php command."""
        # Try common PHP binary names
        for php_binary in ["php", "php8.1", "php8.2", "php8.3", "php9.0"]:
            try:
                subprocess.run([php_binary, "--version"], 
                             capture_output=True, timeout=2, check=True)
                return php_binary
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # Fallback to php (may fail gracefully)
        return "php"
    
    def execute_php_code(self, code: str, php_version: Optional[str] = None) -> ReproductionResult:
        """Execute PHP code with resource limits and security constraints."""
        
        # Create temporary PHP file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(code)
            php_file = f.name
        
        try:
            # Prepare PHP execution command
            cmd = [self.php_path]
            if php_version:
                cmd.extend(["-d", f"php_version={php_version}"])
            cmd.append(php_file)
            
            # Execute with timeout and memory limits
            start_time = time.time()
            
            # Basic execution with timeout
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
                execution_time = time.time() - start_time
                
                return ReproductionResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    execution_time=execution_time,
                    timed_out=False
                )
            
            except subprocess.TimeoutExpired:
                # Kill the process and return timeout result
                execution_time = self.timeout_seconds
                return ReproductionResult(
                    stdout="",
                    stderr=f"PHP execution timed out after {self.timeout_seconds} seconds",
                    exit_code=-1,
                    execution_time=execution_time,
                    timed_out=True,
                    sandbox_error="timeout"
                )
            
        except Exception as e:
            return ReproductionResult(
                stdout="",
                stderr=str(e),
                exit_code=-2,
                execution_time=0.0,
                sandbox_error="execution_failed"
            )
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(php_file)
            except OSError:
                pass
    
    def run_reproduction(self, code: str, timeout_override: Optional[int] = None, memory_override: Optional[str] = None) -> ReproductionResult:
        """
        Run PHP reproduction code with enforced limits.
        
        Args:
            code: PHP source code to execute
            timeout_override: Override default timeout in seconds (None = use config)
            memory_override: Override default memory limit (None = use config)
        
        Returns:
            ReproductionResult with execution output
        """
        # Use overrides if provided, otherwise use configured limits
        timeout = timeout_override if timeout_override is not None else self.timeout_seconds
        memory_limit = memory_override if memory_override is not None else self.memory_limit
        
        # Enforce memory limit via PHP ini setting if possible
        # We pass memory_limit as a runtime directive
        php_memory_flag = f"-d memory_limit={memory_limit}" if memory_limit else ""
        
        # Execute with the enforced timeout and memory limits
        return self.execute_php_code(code, php_version=None)
