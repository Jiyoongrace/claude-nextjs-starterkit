"""
Wiki 검색 Tool 함수 — S4, S6 담당 (RAG).

ChromaDB 연결 시: 벡터 유사도 검색
Mock 모드:        하드코딩 텍스트 반환
"""
from vector.wiki_indexer import search_wiki

# ─── Mock 데이터 (mock-agents.ts S4, S6 데이터와 동일) ──────────────────────
_MOCK_TERM_RESULTS = {
    "단중": {
        "content": (
            "## 타겟 단중 (Target Unit Weight)\n\n"
            "**단중**이란 제품 단위 길이당 무게(kg/m)를 의미합니다.\n"
            "열연 공정에서 타겟 단중은 압연 후 최종 제품의 품질 기준이 됩니다.\n\n"
            "> 관련 에러코드: DG320 (단중 초과 시 발생)"
        ),
        "mappings": [
            {
                "term": "타겟 단중",
                "screen": "품질관리 화면 > 단중 설정 탭",
                "db_table": "TB_SLAB_TARGET",
                "api": "GET /api/slab/target-weight",
            },
            {
                "term": "DG320",
                "screen": "에러 모니터링 대시보드",
                "db_table": "TB_ERROR_LOG",
                "api": "GET /api/errors/DG320",
            },
        ],
    },
}

_MOCK_RUNBOOK_RESULT = {
    "content": (
        "## IRMS 권한 신청 결재 초안 (자동 생성)\n\n"
        "### 결재 라인\n"
        "1. 팀장 승인 → 2. IT 보안 담당자 확인 → 3. 시스템 관리자 등록\n\n"
        "> ⚠️ 위 초안을 검토 후 IRMS 시스템에 직접 등록하세요."
    ),
    "mappings": [],
}


async def search_term(query: str) -> dict:
    """
    비즈니스 용어 또는 에러코드로 Wiki 문서를 검색합니다.

    ChromaDB 연결 시: 벡터 유사도 검색
    Mock 모드:        키워드 매칭 후 하드코딩 결과 반환
    """
    # ChromaDB 벡터 검색 시도
    results = search_wiki(query, n_results=2)
    if results:
        combined_content = "\n\n---\n\n".join(r["content"] for r in results)
        return {"content": combined_content, "mappings": []}

    # Mock 폴백: 키워드 기반 매칭
    query_lower = query.lower()
    for keyword, result in _MOCK_TERM_RESULTS.items():
        if keyword in query_lower or query_lower in keyword:
            return result

    # 기본 폴백
    return {
        "content": f"## {query}\n\n해당 용어에 대한 문서를 찾을 수 없습니다.\nWiki에 새 문서를 추가해주세요.",
        "mappings": [],
    }


async def get_runbook(
    requester: str = "홍길동",
    screen_id: str = "SCR_QUALITY_MGR",
    permission_level: str = "READ_WRITE",
) -> dict:
    """
    IRMS 권한 신청 Runbook을 기반으로 결재 초안을 생성합니다.

    ChromaDB 연결 시: IRMS 런북 문서를 검색하여 동적 생성
    Mock 모드:        하드코딩 결재 초안 반환
    """
    # ChromaDB 런북 검색 시도
    results = search_wiki("IRMS 권한 신청", n_results=1)
    if results:
        runbook_content = results[0]["content"]
        content = (
            f"## IRMS 권한 신청 결재 초안 (자동 생성)\n\n"
            f"**신청자:** {requester}  \n"
            f"**대상 화면 ID:** {screen_id}  \n"
            f"**요청 권한:** {permission_level}\n\n"
            f"### 런북 참조\n\n{runbook_content}"
        )
        return {"content": content, "mappings": []}

    # Mock 폴백
    mock = dict(_MOCK_RUNBOOK_RESULT)
    mock["content"] = (
        f"## IRMS 권한 신청 결재 초안 (자동 생성)\n\n"
        f"**신청 유형:** 신규 화면 접근 권한  \n"
        f"**신청자:** {requester}  \n"
        f"**대상 화면 ID:** {screen_id}  \n"
        f"**요청 권한:** {permission_level}\n\n"
        f"### 신청 사유\n"
        f"업무상 품질관리 화면의 데이터 입력 및 조회 권한이 필요합니다.\n\n"
        f"### 결재 라인\n"
        f"1. 팀장 승인 → 2. IT 보안 담당자 확인 → 3. 시스템 관리자 등록\n\n"
        f"> ⚠️ 위 초안을 검토 후 IRMS 시스템에 직접 등록하세요."
    )
    return mock
