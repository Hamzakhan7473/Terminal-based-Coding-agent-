"""Sandboxed execution environment using E2B."""

import os
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from ..core.models import ExecutionResult, SafetyCheck
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SandboxExecutor:
    """Executes code in a sandboxed environment using E2B."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("E2B_API_KEY")
        self.client = None
        self.current_sandbox = None
        self._init_e2b_client()
    
    def _init_e2b_client(self) -> None:
        """Initialize E2B client."""
        try:
            from e2b_code_interpreter import Sandbox
            self.Sandbox = Sandbox
            logger.info("E2B client initialized successfully")
        except ImportError:
            logger.error("E2B library not installed. Install with: pip install e2b-code-interpreter")
            raise ImportError("E2B library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize E2B client: {e}")
            raise
    
    async def create_sandbox(self, template: str = "base") -> bool:
        """Create a new sandbox environment."""
        try:
            if self.current_sandbox:
                await self.terminate_sandbox()
            
            # Updated E2B API - use create() method
            self.current_sandbox = self.Sandbox.create(api_key=self.api_key)
            logger.info(f"Created E2B code interpreter sandbox")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            return False
    
    async def execute_code(self, code: str, language: str = "python", 
                          timeout: int = 30, files: Optional[Dict[str, str]] = None) -> ExecutionResult:
        """
        Execute code in the sandbox.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            files: Additional files to upload
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Ensure sandbox exists
            if not self.current_sandbox:
                await self.create_sandbox()
            
            # Upload files if provided
            if files:
                await self._upload_files(files)
            
            # Perform safety check
            safety_check = self._check_code_safety(code, language)
            if not safety_check.is_safe:
                logger.warning(f"Code failed safety check: {safety_check.warnings}")
                return ExecutionResult(
                    success=False,
                    stderr=f"Code failed safety check: {', '.join(safety_check.warnings)}",
                    exit_code=1,
                    execution_time=time.time() - start_time
                )
            
            # Execute code based on language
            if language.lower() == "python":
                result = await self._execute_python(code, timeout)
            elif language.lower() in ["javascript", "js"]:
                result = await self._execute_javascript(code, timeout)
            elif language.lower() in ["bash", "shell"]:
                result = await self._execute_shell(code, timeout)
            else:
                result = await self._execute_generic(code, language, timeout)
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=1,
                execution_time=time.time() - start_time
            )
    
    async def _upload_files(self, files: Dict[str, str]) -> None:
        """Upload files to sandbox."""
        try:
            for file_path, content in files.items():
                # Use E2B code interpreter's filesystem API
                self.current_sandbox.filesystem.write(file_path, content)
                
            logger.info(f"Uploaded {len(files)} files to sandbox")
            
        except Exception as e:
            logger.error(f"Failed to upload files: {e}")
            raise
    
    async def _execute_python(self, code: str, timeout: int) -> ExecutionResult:
        """Execute Python code."""
        try:
            # Use E2B code interpreter's run_code method
            execution = self.current_sandbox.run_code(code)
            
            # Collect output
            stdout_text = ""
            stderr_text = ""
            
            if hasattr(execution, 'logs'):
                if hasattr(execution.logs, 'stdout'):
                    stdout_text = "\n".join([str(log) for log in execution.logs.stdout])
                if hasattr(execution.logs, 'stderr'):
                    stderr_text = "\n".join([str(log) for log in execution.logs.stderr])
            
            if hasattr(execution, 'results'):
                for result in execution.results:
                    if hasattr(result, 'text'):
                        stdout_text += f"\n{result.text}"
                    else:
                        stdout_text += f"\n{result}"
            
            success = not execution.error if hasattr(execution, 'error') else True
            if hasattr(execution, 'error') and execution.error:
                stderr_text += f"\n{execution.error.name}: {execution.error.value}"
            
            return ExecutionResult(
                success=success,
                stdout=stdout_text.strip(),
                stderr=stderr_text.strip(),
                exit_code=0 if success else 1
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=1
            )
    
    async def _execute_javascript(self, code: str, timeout: int) -> ExecutionResult:
        """Execute JavaScript code."""
        try:
            # Write code to temporary file
            temp_file = "/tmp/execution.js"
            await self.current_sandbox.filesystem.write(temp_file, code)
            
            # Execute the file
            process = await self.current_sandbox.process.start(
                f"node {temp_file}",
                timeout=timeout
            )
            
            await process.wait()
            
            return ExecutionResult(
                success=process.exit_code == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.exit_code
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=1
            )
    
    async def _execute_shell(self, code: str, timeout: int) -> ExecutionResult:
        """Execute shell commands."""
        try:
            process = await self.current_sandbox.process.start(
                code,
                timeout=timeout
            )
            
            await process.wait()
            
            return ExecutionResult(
                success=process.exit_code == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.exit_code
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=1
            )
    
    async def _execute_generic(self, code: str, language: str, timeout: int) -> ExecutionResult:
        """Execute code in generic way."""
        try:
            # Create temporary file with appropriate extension
            ext_map = {
                "java": ".java",
                "cpp": ".cpp",
                "c": ".c",
                "rust": ".rs",
                "go": ".go"
            }
            
            ext = ext_map.get(language.lower(), ".txt")
            temp_file = f"/tmp/execution{ext}"
            
            await self.current_sandbox.filesystem.write(temp_file, code)
            
            # Try to execute based on language
            if language.lower() == "java":
                # Compile first
                compile_process = await self.current_sandbox.process.start(
                    f"javac {temp_file}",
                    timeout=timeout
                )
                await compile_process.wait()
                
                if compile_process.exit_code != 0:
                    return ExecutionResult(
                        success=False,
                        stderr=compile_process.stderr,
                        exit_code=compile_process.exit_code
                    )
                
                # Execute compiled class
                class_name = "execution"
                process = await self.current_sandbox.process.start(
                    f"java {class_name}",
                    timeout=timeout
                )
            else:
                # For other languages, try direct execution
                process = await self.current_sandbox.process.start(
                    f"timeout {timeout} {language} {temp_file}",
                    timeout=timeout
                )
            
            await process.wait()
            
            return ExecutionResult(
                success=process.exit_code == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.exit_code
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=1
            )
    
    def _check_code_safety(self, code: str, language: str) -> SafetyCheck:
        """Perform safety checks on code before execution."""
        warnings = []
        blocked_operations = []
        security_concerns = []
        
        # Dangerous imports/operations
        dangerous_patterns = {
            "python": [
                "import os", "import subprocess", "import sys", "__import__",
                "exec(", "eval(", "compile(", "open(", "file(",
                "socket", "urllib", "requests", "http.client"
            ],
            "javascript": [
                "require(", "import(", "eval(", "Function(",
                "process", "fs", "child_process", "http", "https"
            ],
            "bash": [
                "rm -rf", "dd if=", "mkfs", "format", "fdisk",
                "chmod 777", "chown", "su ", "sudo ", "passwd"
            ]
        }
        
        patterns = dangerous_patterns.get(language.lower(), [])
        
        for pattern in patterns:
            if pattern in code.lower():
                if pattern in ["import os", "import subprocess", "import sys"]:
                    warnings.append(f"Potentially dangerous import: {pattern}")
                else:
                    blocked_operations.append(pattern)
                    security_concerns.append(f"Blocked dangerous operation: {pattern}")
        
        # Resource limits
        resource_limits = {
            "max_execution_time": 30,
            "max_memory": "512MB",
            "max_files": 10
        }
        
        is_safe = len(blocked_operations) == 0
        
        return SafetyCheck(
            is_safe=is_safe,
            warnings=warnings,
            blocked_operations=blocked_operations,
            resource_limits=resource_limits,
            security_concerns=security_concerns
        )
    
    async def get_sandbox_info(self) -> Dict[str, Any]:
        """Get information about current sandbox."""
        if not self.current_sandbox:
            return {"status": "No sandbox active"}
        
        try:
            # Get basic system info
            process = await self.current_sandbox.process.start("uname -a")
            await process.wait()
            
            return {
                "status": "active",
                "system_info": process.stdout.strip(),
                "template": getattr(self.current_sandbox, 'template', 'unknown')
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def terminate_sandbox(self) -> bool:
        """Terminate current sandbox."""
        try:
            if self.current_sandbox:
                self.current_sandbox.kill()
                self.current_sandbox = None
                logger.info("Sandbox terminated successfully")
                return True
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate sandbox: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.create_sandbox()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.terminate_sandbox()
