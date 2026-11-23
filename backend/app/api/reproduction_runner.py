"""Reproduction runner request/response models for API."""

from pydantic import BaseModel, Field
from typing import Optional


class ReproductionRunRequest(BaseModel):
    """Request to run PHP code in sandbox."""
    code: str = Field(..., description="PHP source code to execute")
    timeout: Optional[int] = Field(None, description="Timeout in seconds (overrides default)")
    memory_limit: Optional[str] = Field(None, description="Memory limit override (e.g. '128m')")


class ReproductionRunResponse(BaseModel):
    """Response from running PHP code in sandbox."""
    stdout: str = Field(..., description=" captured stdout")
    stderr: str = Field(..., description=" captured stderr")
    exit_code: int = Field(..., description="process exit code")
    execution_time: float = Field(..., description="execution time in seconds")
    timed_out: bool = Field(..., description="whether execution timed out")
    sandbox_error: Optional[str] = Field(None, description="sandbox error if any")
