import os
from typing import Optional

# neo4j 패키지가 없을 경우를 대비한 안전한 임포트
try:
    from neo4j import AsyncGraphDatabase, AsyncDriver
    _NEO4J_AVAILABLE = True
except ImportError:
    _NEO4J_AVAILABLE = False
    AsyncDriver = None  # type: ignore

_driver: Optional[object] = None


async def init_driver() -> None:
    """
    FastAPI lifespan에서 호출.
    연결 실패 또는 Mock 모드여도 앱 시작은 정상 진행.
    """
    global _driver

    use_mock = os.getenv("USE_NEO4J_MOCK", "true").lower() == "true"
    uri = os.getenv("NEO4J_URI", "")

    if use_mock or not uri or not _NEO4J_AVAILABLE:
        print("[Neo4j] Mock 모드 — 실제 DB 연결 없음")
        return

    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")

    try:
        _driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        await _driver.verify_connectivity()  # type: ignore
        print(f"[Neo4j] 연결 성공: {uri}")
    except Exception as e:
        print(f"[Neo4j] 연결 실패 → Mock 데이터 사용: {e}")
        _driver = None


def get_driver() -> Optional[object]:
    """None이면 Mock 모드. Tool 함수에서 if get_driver() is None: 으로 분기."""
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()  # type: ignore
        _driver = None
