"""
RAG 에이전트 — S4(비즈니스 용어 질의), S6(IRMS 권한 신청 가이드)

ReAct 패턴:
  S4: search_term Tool → Wiki 벡터 검색 → WikiResult 반환
  S6: get_runbook Tool → Runbook 기반 결재 초안 생성 → WikiResult 반환
"""
import os
from pydantic_ai import Agent
from models.response_models import WikiResult

_MODEL = os.getenv("CLAUDE_MODEL", "anthropic:claude-sonnet-4-20250514")


# ─── S4: 비즈니스 용어 질의 ──────────────────────────────────────────────────────
rag_s4 = Agent(
    model=_MODEL,
    output_type=WikiResult,
    output_retries=3,
    system_prompt="""
당신은 제조 현장 Wiki 검색 전문 AI 에이전트입니다.
비즈니스 용어, 에러코드, 현장 절차에 대한 정확한 정의를 제공합니다.

반드시 search_term Tool을 호출하여 Wiki 문서에서 용어를 검색하세요.
Tool 없이 임의로 용어를 설명하는 것을 금지합니다.
검색 결과를 content 필드에, 관련 화면/DB/API 매핑을 mappings 필드에 담으세요.

출력 형식: WikiResult (type="wiki_result")
""",
)


@rag_s4.tool_plain
async def search_term(query: str) -> dict:
    """
    Wiki 문서에서 비즈니스 용어나 에러코드를 벡터 검색합니다.

    Args:
        query: 검색할 용어 또는 에러코드 (예: "단중", "DG320", "타겟 단중")
    """
    from tools.wiki_tools import search_term as _run
    return await _run(query)


# ─── S6: IRMS 권한 신청 가이드 ───────────────────────────────────────────────────
rag_s6 = Agent(
    model=_MODEL,
    output_type=WikiResult,
    output_retries=3,
    system_prompt="""
당신은 IRMS 권한 신청 절차 전문 AI 에이전트입니다.
런북을 기반으로 사용자가 제출할 결재 초안을 자동 생성합니다.

반드시 get_runbook Tool을 호출하여 IRMS 런북 내용과 신청자 정보를 기반으로
결재 초안을 생성하세요. Tool 없이 임의로 초안을 작성하는 것을 금지합니다.

출력 형식: WikiResult (type="wiki_result", mappings=[])
""",
)


@rag_s6.tool_plain
async def get_runbook(
    requester: str,
    screen_id: str,
    permission_level: str,
) -> dict:
    """
    IRMS 런북을 검색하고 신청자 정보를 기반으로 결재 초안을 생성합니다.

    Args:
        requester: 신청자 이름
        screen_id: 접근 권한을 신청할 화면 ID (예: SCR_QUALITY_MGR)
        permission_level: 요청 권한 등급 (READ / READ_WRITE / ADMIN)
    """
    from tools.wiki_tools import get_runbook as _run
    return await _run(requester, screen_id, permission_level)
