"""Health check tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "signal-hub-alan-vo"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "signal-hub-alan-vo"
        assert data["author"] == "Alan Vo <alanvo@gmail.com>"


@pytest.mark.asyncio
async def test_issue_analysis_jit_segfault():
    """Test JIT segfault classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "JIT segmentation fault in PHP 8.1",
            "body": "PHP 8.1.0 produces segfault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER",
            "php_version": "8.1.0",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "jit_segfault"
        assert data["confidence"] >= 0.8
        assert 7817 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_gc_threshold():
    """Test GC threshold performance classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "Bad performance with hard-coded GC_THRESHOLD values",
            "body": "PHPUnit tests slowed down between 8.1.9 and 8.1.10",
            "php_version": "8.1.10",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "gc_threshold"
        assert 9993 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_fork_safety():
    """Test macOS fork safety classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "macOS now crashes fork() process",
            "body": "objc[54119]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called",
            "php_version": "8.2.8",
            "os": "macOS 13.5",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "fork_safety"
        assert 11818 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_array_unique():
    """Test array_unique SORT_REGULAR classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "array_unique() with SORT_REGULAR returns duplicate values",
            "body": "Non-transitive comparison in zendi_smart_strcmp causes duplicates to not be grouped",
            "php_version": "8.4.13",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "array_unique"
        assert 20262 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_ldap_cleanup():
    """Test LDAP cleanup segfault classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "Segmentation fault on exit when using ldap_bind()",
            "body": "ENGINE_remove in eng_list.c during curl_global_cleanup after ldap_bind failure",
            "php_version": "7.4.28",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "ldap_cleanup"
        assert 8620 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_unknown():
    """Test unknown issue classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/issues/analyze", json={
            "title": "Random unrelated issue",
            "body": "This is not a known PHP interpreter bug pattern",
            "php_version": "8.3.0",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "unknown"
        assert data["confidence"] == 0.0


@pytest.mark.asyncio
async def test_issue_types_list():
    """Test issue types enumeration endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/issues/types")
        assert response.status_code == 200
        data = response.json()
        assert "jit_segfault" in data
        assert "gc_threshold" in data
        assert "fork_safety" in data
        assert "array_unique" in data
        assert "ldap_cleanup" in data
        assert "unknown" in data