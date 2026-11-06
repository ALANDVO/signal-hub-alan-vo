"""Issues API endpoints for PHP issue analysis and history."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.database import get_db, IssueAnalysis as IssueAnalysisModel

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
    id: Optional[int] = None
    issue_type: IssueType
    confidence: float
    reproduction_hints: List[str]
    related_issues: List[int]


@router.post("/issues/analyze", response_model=IssueAnalysisResponse, tags=["issues"])
async def analyze_issue(request: IssueAnalysisRequest, db: AsyncSession = Depends(get_db)):
    """
    Analyze a PHP issue report and classify the issue type.
    Stores the analysis in history.
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
        confidence = 0.95
        reproduction_hints = [
            "Test with PHP 8.2+ and OpenLDAP",
            "Check for use-after-free in engine list cleanup",
            "Verify SSL/TLS connection cleanup order",
        ]
        related_issues = [8620]
    
    # array_unique SORT_REGULAR bug
    elif any(kw in text for kw in ["array_unique", "sort_regular", "duplicate", "non-transitive", "zendi_smart_strcmp"]):
        issue_type = IssueType.ARRAY_UNIQUE
        confidence = 0.90
        reproduction_hints = [
            "Test array_unique with SORT_REGULAR flag",
            "Compare string vs integer key handling",
            "Check for non-transitive comparison behavior",
        ]
        related_issues = [20262]
    
    # Fork safety (macOS)
    elif any(kw in text for kw in ["fork", "objc_initializeafterforkerror", "nsplaceholderdate", "macos", "sigabrt"]):
        issue_type = IssueType.FORK_SAFETY
        confidence = 0.88
        reproduction_hints = [
            "Test on macOS with fork()",
            "Set OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES",
            "Check for NSPlaceholderDate initialization after fork",
        ]
        related_issues = [11818]
    
    # GC threshold performance
    elif any(kw in text for kw in ["gc_threshold", "gc performance", "phpunit slow", "garbage collection"]):
        issue_type = IssueType.GC_THRESHOLD
        confidence = 0.85
        reproduction_hints = [
            "Run phpunit test suite with gc_collect_cycles()",
            "Monitor GC threshold values",
            "Test with GC_DISABLE=1",
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
    
    # Store in history first to get the ID
    analysis_record = IssueAnalysisModel(
        issue_type=issue_type.value,
        confidence=confidence,
        title=request.title,
        body=request.body,
        php_version=request.php_version,
        os=request.os,
        reproduction_hints=json.dumps(reproduction_hints),
        related_issues=json.dumps(related_issues),
    )
    db.add(analysis_record)
    await db.commit()
    await db.refresh(analysis_record)
    
    return IssueAnalysisResponse(
        id=analysis_record.id,
        issue_type=issue_type,
        confidence=confidence,
        reproduction_hints=reproduction_hints,
        related_issues=related_issues,
    )


@router.get("/issues/history", response_model=List[IssueAnalysisResponse], tags=["issues"])
async def get_issue_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    issue_type: Optional[str] = Query(None, description="Filter by issue type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated issue analysis history.
    """
    query = select(IssueAnalysisModel).order_by(desc(IssueAnalysisModel.created_at))
    
    if issue_type:
        query = query.where(IssueAnalysisModel.issue_type == issue_type)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [
        IssueAnalysisResponse(
            id=record.id,
            issue_type=IssueType(record.issue_type),
            confidence=record.confidence,
            reproduction_hints=json.loads(record.reproduction_hints),
            related_issues=json.loads(record.related_issues),
        )
        for record in records
    ]


@router.get("/issues/history/{analysis_id}", response_model=IssueAnalysisResponse, tags=["issues"])
async def get_issue_history_by_id(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single issue analysis by ID.
    """
    result = await db.execute(
        select(IssueAnalysisModel).where(IssueAnalysisModel.id == analysis_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return IssueAnalysisResponse(
        id=record.id,
        issue_type=IssueType(record.issue_type),
        confidence=record.confidence,
        reproduction_hints=json.loads(record.reproduction_hints),
        related_issues=json.loads(record.related_issues),
    )


@router.get("/issues/types", response_model=List[IssueType], tags=["issues"])
async def list_issue_types():
    """List all known issue types."""
    return list(IssueType)
