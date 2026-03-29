"""
Neo4j 그래프 탐색 Tool 함수 — S5 담당.

⚠️ 교체 포인트 (Phase 2):
    get_driver() is not None 상태가 되면 자동으로 실제 Cypher 쿼리 경로 실행.
    USE_NEO4J_MOCK=false + NEO4J_URI 설정만으로 교체 완료.
"""
from graph.neo4j_client import get_driver

# ─── Mock 데이터 (mock-agents.ts S5 데이터와 동일) ──────────────────────────
_MOCK_FACTORY_GRAPH = {
    "nodes": [
        {"id": "1", "label": "신규 열연공장\n(HOT_MILL_3)", "type": "target"},
        {"id": "2", "label": "공장 마스터 DB\n(TB_PLANT_MST)", "type": "db"},
        {"id": "3", "label": "생산계획 서비스\n(PlanningAPI)", "type": "service"},
        {"id": "4", "label": "단중 계산 모듈\n(WeightCalc)", "type": "code"},
        {"id": "5", "label": "Edging 기준 테이블\n(TB_EDGE)", "type": "db"},
        {"id": "6", "label": "리포트 생성기\n(ReportGen)", "type": "code"},
    ],
    "edges": [
        {"source": "1", "target": "2", "label": "등록 필요"},
        {"source": "2", "target": "3", "label": "FK 참조"},
        {"source": "3", "target": "4", "label": "호출"},
        {"source": "3", "target": "5", "label": "조회"},
        {"source": "4", "target": "6", "label": "결과 전달"},
    ],
}


async def traverse_factory_impact(factory_name: str, target_systems: list[str]) -> dict:
    """
    신규 공장 추가 시 영향받는 소스 컴포넌트를 그래프 탐색합니다.

    Neo4j 연결 시: MATCH path = (:Factory {id: $factory})-[*1..5]->() 실행
    Mock 모드:    하드코딩 그래프 데이터 반환

    ⚠️ 교체 포인트: Neo4j AuraDB 연결 후 아래 Cypher 쿼리 활성화
    """
    driver = get_driver()
    if driver is None:
        # ⚠️ Mock 반환
        return _MOCK_FACTORY_GRAPH

    # 실제 Neo4j 경로 (교체 후 동작)
    async with driver.session() as session:  # type: ignore
        result = await session.run(
            """
            MATCH path = (f:Factory {id: $factory_id})-[*1..5]->(component)
            RETURN
              [n IN nodes(path) | {id: id(n), label: coalesce(n.name, n.id), type: labels(n)[0]}] AS nodes,
              [r IN relationships(path) | {source: startNode(r).id, target: endNode(r).id, label: type(r)}] AS edges
            LIMIT 20
            """,
            factory_id=factory_name,
        )
        records = [record.data() async for record in result]
        if not records:
            return _MOCK_FACTORY_GRAPH
        return {"nodes": records[0]["nodes"], "edges": records[0]["edges"]}
