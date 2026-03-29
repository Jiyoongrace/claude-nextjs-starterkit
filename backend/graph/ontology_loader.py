"""
Neo4j 온톨로지 초기 데이터 로더.
OT DB 연동 승인 전까지는 하드코딩 데이터로 AuraDB를 초기화합니다.
연동 승인 후: 이 파일의 MERGE Cypher를 실제 DB 스키마 파싱으로 교체.
"""
from graph.neo4j_client import get_driver

# DG320 에러 → TB_SLAB_TARGET → PlanningAPI → SCR_QUALITY_MGR 경로
INITIAL_ONTOLOGY_CYPHER = """
MERGE (e1:ErrorCode {id: 'DG320', description: '단중 초과 에러'})
MERGE (t1:DBTable {id: 'TB_SLAB_TARGET', columns: 'slab_id,target_weight'})
MERGE (t2:DBTable {id: 'TB_ERROR_LOG', columns: 'error_id,error_code,occurred_at'})
MERGE (t3:DBTable {id: 'TB_EDGE_SPEC', columns: 'spec_id,press_amount,thickness_tolerance'})
MERGE (s1:Service {id: 'PlanningAPI', endpoint: '/api/slab/plan'})
MERGE (s2:Service {id: 'OrderAPI', endpoint: '/api/orders'})
MERGE (s3:Service {id: 'WeightCalc', endpoint: '/api/weight/calc'})
MERGE (sc1:Screen {id: 'SCR_QUALITY_MGR', name: '품질관리 화면'})
MERGE (sc2:Screen {id: 'SCR_ERROR_MONITOR', name: '에러 모니터링 대시보드'})
MERGE (g1:GitCommit {hash: 'b71e4d8', message: '단중 허용 범위 상수값 변경 (320→295)', author: 'lee.dev', date: '2025-03-25'})
MERGE (f1:Factory {id: 'HOT_MILL_3', name: '신규 열연공장 3호기'})

MERGE (e1)-[:CAUSED_BY]->(t1)
MERGE (t1)-[:QUERIED_BY]->(s1)
MERGE (s1)-[:DISPLAYED_ON]->(sc1)
MERGE (t1)-[:CHANGED_BY]->(g1)
MERGE (e1)-[:LOGGED_IN]->(t2)
MERGE (t2)-[:DISPLAYED_ON]->(sc2)
MERGE (f1)-[:REGISTERS_IN]->(t1)
MERGE (t1)-[:REFERENCED_BY]->(s1)
MERGE (s1)-[:CALLS]->(s3)
"""


async def load_initial_ontology() -> None:
    """서버 시작 시 Neo4j 연결이 있을 때만 실행."""
    driver = get_driver()
    if driver is None:
        return  # Mock 모드에서는 실행하지 않음

    async with driver.session() as session:  # type: ignore
        await session.run(INITIAL_ONTOLOGY_CYPHER)
        print("[Neo4j] 온톨로지 초기 데이터 로드 완료")
