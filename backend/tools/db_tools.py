"""
DB 조회 Tool 함수 — S7 담당 (크로스 DB 불일치 탐지).

⚠️ 교체 포인트 (Phase 3):
    OT DB 연동 승인 후 get_order_data(), get_production_data()를
    실제 DB 쿼리로 교체. 함수 시그니처는 동일하게 유지.
"""


async def get_order_data(service_a: str = "ORDER_DB") -> list[dict]:
    """
    주문 서비스 DB에서 현재 대기 중인 주문 데이터를 조회합니다.

    ⚠️ Mock 구현 — 하드코딩 ORDER_DB 데이터
    교체 대상:
        async with get_db_connection("ORDER_DB") as conn:
            rows = await conn.fetch(
                "SELECT order_id, slab_id, status, qty::text FROM TB_ORDER WHERE status = 'WAITING'"
            )
            return [dict(row) for row in rows]
    """
    return [
        {"order_id": "ORD-001", "slab_id": "SLB-101", "status": "WAITING", "qty": "150"},
        {"order_id": "ORD-002", "slab_id": "SLB-102", "status": "WAITING", "qty": "200"},
        {"order_id": "ORD-003", "slab_id": "SLB-103", "status": "WAITING", "qty": "180"},
    ]


async def get_production_data(service_b: str = "PROD_DB") -> list[dict]:
    """
    생산 서비스 DB에서 동일 주문에 대한 생산 상태 데이터를 조회합니다.

    ⚠️ Mock 구현 — 하드코딩 PROD_DB 데이터 (의도적 불일치 포함)
    교체 대상:
        async with get_db_connection("PROD_DB") as conn:
            rows = await conn.fetch(
                "SELECT order_id, slab_id, status, qty::text FROM TB_PRODUCTION"
            )
            return [dict(row) for row in rows]
    """
    return [
        {"order_id": "ORD-001", "slab_id": "SLB-101", "status": "IN_PROGRESS", "qty": "150"},  # status 불일치
        {"order_id": "ORD-002", "slab_id": "SLB-102", "status": "WAITING", "qty": "200"},
        {"order_id": "ORD-003", "slab_id": "SLB-103", "status": "COMPLETED", "qty": "95"},    # status + qty 불일치
    ]


def find_diff_keys(rows_a: list[dict], rows_b: list[dict]) -> list[str]:
    """두 테이블에서 실제로 값이 다른 컬럼 키를 반환합니다."""
    if not rows_a or not rows_b:
        return []

    diff_keys: set[str] = set()
    for row_a, row_b in zip(rows_a, rows_b):
        for key in row_a:
            if key in row_b and row_a[key] != row_b[key]:
                diff_keys.add(key)
    return list(diff_keys)
