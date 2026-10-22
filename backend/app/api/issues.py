"""Issues API endpoints - placeholder for issue analysis."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

router = APIRouter()


class IssueType(str, Enum):
    """Known PHP issue types from php-src."""
    JIT_SEGFAULT = "jit_segfault"
    GC_THRESHOLD = "gc_threshold"
    FORK_SAFETY = "fork_safety"
    ARRAY_UNIQUE = "array_unique"
    LDAP_CLEANUP = "ldap_cleanup"
    UNKNOWN = "unknown"


class IssueAnalysisRequest(BaseModel):
    """Request to analyze a PHP issue report."""
    title: str
    body: str
    php_version: Optional[str] = None
    os: Optional[str] = None


class IssueAnalysisResponse(BaseModel):
    """Response with classified issue type and hints."""
    issue_type: IssueType
    confidence: float
    reproduction_hints: List[str]
    related_issues: List[int]


@router.post("/issues/analyze", response_model=IssueAnalysisResponse, tags=["issues"])
async def analyze_issue(request: IssueAnalysisRequest):
    """
    Analyze a PHP issue report and classify the failure type.
    
    Uses deterministic pattern matching on issue title/body to identify
    known PHP interpreter bug categories.
    """
    # Deterministic classification based on keywords
    text = (request.title + " " + request.body).lower()
    
    issue_type = IssueType.UNKNOWN
    confidence = 0.0
    reproduction_hints = []
    related_issues = []
    
    # LDAP cleanup segfault - check first (most specific terms)
    if any(kw in text for kw in ["ldap_bind", "engineremove", "enginelistcleanup", "curl_global_cleanup", "ossl_cleanup"]):
        issue_type = IssueType.LDAP_CLEANUP
        confidence = 0.85
        reproduction_hints = [
            "Test: ldap_connect + ldap_bind with invalid credentials",
            "Check OpenSSL engine cleanup order",
            "Test on PHP 7.4 and 8.0",
        ]
        related_issues = [8620]
    
    # array_unique SORT_REGULAR bug
    elif any(kw in text for kw in ["array_unique", "sort_regular", "duplicate", "non-transitive", "zendi_smart_strcmp"]):
        issue_type = IssueType.ARRAY_UNIQUE
        confidence = 0.95
        reproduction_hints = [
            "Test: array_unique(['5', '10', '5', '3A', '5'], SORT_REGULAR)",
            "Compare with SORT_STRING behavior",
            "Check for mixed numeric/non-numeric strings",
        ]
        related_issues = [20262]
    
    # Fork safety (macOS)
    elif any(kw in text for kw in ["fork", "objc_initializeafterforkerror", "nsplaceholderdate", "macos", "sigabrt"]):
        issue_type = IssueType.FORK_SAFETY
        confidence = 0.90
        reproduction_hints = [
            "Test on macOS 13.5+",
            "Use php-fpm with multiple workers",
            "Set OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES as workaround",
        ]
        related_issues = [11818]
    
    # GC threshold performance
    elif any(kw in text for kw in ["gc_threshold", "gc performance", "phpunit slow", "garbage collection"]):
        issue_type = IssueType.GC_THRESHOLD
        confidence = 0.80
        reproduction_hints = [
            "Run large test suite with many objects",
            "Compare PHP 8.1.9 vs 8.1.10+",
            "Monitor GC cycles with gc_status()",
        ]
        related_issues = [9993]
    
    # JIT segfault patterns - check last (generic "segfault" term)
    elif any(kw in text for kw in ["jit", "segfault", "segmentation fault", "zend_new_spec", "zend_vm_execute"]):
        issue_type = IssueType.JIT_SEGFAULT
        confidence = 0.85
        reproduction_hints = [
            "Enable JIT: opcache.jit=tracing",
            "Test with PHP 8.1.x",
            "Check for ZEND_NEW_SPEC_CONST_UNUSED_HANDLER in backtrace",
        ]
        related_issues = [7817]
    
    return IssueAnalysisResponse(
        issue_type=issue_type,
        confidence=confidence,
        reproduction_hints=reproduction_hints,
        related_issues=related_issues,
    )


@router.get("/issues/types", response_model=List[IssueType], tags=["issues"])
async def list_issue_types():
    """List all known issue types."""
    return list(IssueType)