# TypeScript RichRenderer AgentResponse 타입과 1:1 대응하는 Pydantic 모델
# 변경 시 src/components/agent/RichRenderer/index.tsx의 AgentResponse 타입도 함께 수정 필요

from pydantic import BaseModel
from typing import Literal, Union


class SimulationResult(BaseModel):
    """S1: DG320 에러 방지 파라미터 탐색 결과"""
    type: Literal["simulation_table"]
    title: str
    params: dict[str, str]
    results: list[dict[str, str]]   # 한국어 키 허용 (시도, 폭, 두께 등)
    optimal_index: int


class TimelineItem(BaseModel):
    name: str
    before: int | float
    after: int | float


class RippleEffectResult(BaseModel):
    """S2: Edging 기준 변경 파생 효과 — Mermaid 다이어그램 + 시계열 차트"""
    type: Literal["ripple_effect"]
    title: str
    diagram: str                    # Mermaid graph LR 문법 문자열
    timeline: list[TimelineItem]


class GitCommit(BaseModel):
    hash: str
    message: str
    author: str
    date: str
    is_suspect: bool


class GitTimelineResult(BaseModel):
    """S3: Git 커밋 타임라인 — 의심 커밋 탐지"""
    type: Literal["git_timeline"]
    title: str
    commits: list[GitCommit]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str   # "target" | "db" | "service" | "code"


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class GraphPathResult(BaseModel):
    """S5: 온톨로지 노드-엣지 경로 시각화 (ReactFlow)"""
    type: Literal["graph_path"]
    title: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class WikiMapping(BaseModel):
    term: str
    screen: str
    db_table: str
    api: str


class WikiResult(BaseModel):
    """S4, S6: Wiki 문서 + 화면↔DB↔API 매핑 테이블"""
    type: Literal["wiki_result"]
    content: str                    # 마크다운 본문
    mappings: list[WikiMapping]


class MsaDiffResult(BaseModel):
    """S7: 두 DB 쿼리 결과 좌우 대비 — 불일치 행 강조"""
    type: Literal["msa_diff"]
    title: str
    service_a: str
    service_b: str
    rows_a: list[dict[str, str]]
    rows_b: list[dict[str, str]]
    diff_keys: list[str]            # 불일치 컬럼 (빨간 하이라이트 대상)


# FastAPI response_model 및 PydanticAI result_type에서 사용하는 유니온 타입
# Pydantic v2 discriminated union — type 필드로 자동 모델 선택
AgentResponse = Union[
    SimulationResult,
    RippleEffectResult,
    GitTimelineResult,
    GraphPathResult,
    WikiResult,
    MsaDiffResult,
]
