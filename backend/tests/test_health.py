"""Health check and issue analysis tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.database import init_db


@pytest.fixture(autouse=True, scope="session")
async def initialize_database():
    """Initialize database before tests."""
    await init_db()


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
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
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "JIT segfault in PHP 8.2",
                "body": "Segmentation fault when enabling opcache.jit=tracing",
                "php_version": "8.2.10",
                "os": "Linux",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "jit_segfault"
        assert data["confidence"] == 0.85
        assert 7817 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_gc_threshold():
    """Test GC threshold performance classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "GC threshold performance regression",
                "body": "phpunit slow due to garbage collection threshold changes",
                "php_version": "8.1.0",
                "os": "Linux",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "gc_threshold"
        assert data["confidence"] == 0.85
        assert 9993 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_fork_safety():
    """Test macOS fork safety classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "Fork safety issue on macOS",
                "body": "objc_initializeAfterForkError with NSPlaceholderDate causing SIGABRT",
                "php_version": "8.2.0",
                "os": "macOS",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "fork_safety"
        assert data["confidence"] == 0.88
        assert 11818 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_array_unique():
    """Test array_unique SORT_REGULAR classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "array_unique bug with SORT_REGULAR",
                "body": "Duplicate values not removed with SORT_REGULAR flag, non-transitive comparison",
                "php_version": "8.3.0",
                "os": "Linux",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "array_unique"
        assert data["confidence"] == 0.90
        assert 20262 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_ldap_cleanup():
    """Test LDAP cleanup segfault classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "LDAP cleanup segfault",
                "body": "Segmentation fault during ldap_bind and engine list cleanup with curl_global_cleanup",
                "php_version": "8.2.5",
                "os": "Linux",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "ldap_cleanup"
        assert data["confidence"] == 0.95
        assert 8620 in data["related_issues"]


@pytest.mark.asyncio
async def test_issue_analysis_unknown():
    """Test unknown issue classification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "Random issue",
                "body": "This is some random issue with no known patterns",
                "php_version": "8.2.0",
                "os": "Linux",
            },
        )
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


@pytest.mark.asyncio
async def test_issue_history_empty():
    """Test issue history returns empty list initially."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/issues/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_issue_history_after_analysis():
    """Test issue history stores and retrieves analyses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create an analysis
        await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "Test JIT segfault",
                "body": "Segmentation fault with JIT enabled",
                "php_version": "8.2.0",
                "os": "Linux",
            },
        )
        
        # Get history
        response = await client.get("/api/v1/issues/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["issue_type"] == "jit_segfault"
        assert data[0]["confidence"] == 0.85
        assert 7817 in data[0]["related_issues"]


@pytest.mark.asyncio
async def test_issue_history_pagination():
    """Test issue history pagination."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create multiple analyses
        for i in range(3):
            await client.post(
                "/api/v1/issues/analyze",
                json={
                    "title": f"Test issue {i}",
                    "body": "JIT segfault test",
                    "php_version": "8.2.0",
                    "os": "Linux",
                },
            )
        
        # Get first page
        response = await client.get("/api/v1/issues/history?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Get second page
        response = await client.get("/api/v1/issues/history?page=2&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


@pytest.mark.asyncio
async def test_issue_history_filter_by_type():
    """Test issue history filtering by issue type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create analyses of different types
        await client.post(
            "/api/v1/issues/analyze",
            json={"title": "JIT test", "body": "JIT segfault", "php_version": "8.2.0", "os": "Linux"},
        )
        await client.post(
            "/api/v1/issues/analyze",
            json={"title": "GC test", "body": "GC threshold performance", "php_version": "8.2.0", "os": "Linux"},
        )
        
        # Filter by jit_segfault
        response = await client.get("/api/v1/issues/history?issue_type=jit_segfault")
        assert response.status_code == 200
        data = response.json()
        assert all(item["issue_type"] == "jit_segfault" for item in data)
        
        # Filter by gc_threshold
        response = await client.get("/api/v1/issues/history?issue_type=gc_threshold")
        assert response.status_code == 200
        data = response.json()
        assert all(item["issue_type"] == "gc_threshold" for item in data)


@pytest.mark.asyncio
async def test_issue_history_by_id():
    """Test getting single analysis by ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create an analysis
        create_response = await client.post(
            "/api/v1/issues/analyze",
            json={
                "title": "Test for ID lookup",
                "body": "JIT segfault test",
                "php_version": "8.2.0",
                "os": "Linux",
            },
        )
        assert create_response.status_code == 200
        
        # Get history to find the ID
        history_response = await client.get("/api/v1/issues/history")
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) >= 1
        
        # Get by ID (the most recent should be first)
        analysis_id = history[0]["id"]
        response = await client.get(f"/api/v1/issues/history/{analysis_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["issue_type"] == "jit_segfault"
        assert data["confidence"] == 0.85
        assert data["id"] == analysis_id


@pytest.mark.asyncio
async def test_issue_history_not_found():
    """Test 404 for non-existent analysis ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/issues/history/999999")
        assert response.status_code == 404
