"""
제조 현장 AI 에이전트 백본 시스템 — FastAPI 진입점

실행:
    cd backend
    uv run uvicorn main:app --reload --port 8000

포트:
    8000 — FastAPI 백엔드 (이 파일)
    3000 — Next.js 프론트엔드
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.request_models import AgentRunRequest
from agents.orchestrator import run_scenario
from graph.neo4j_client import init_driver, close_driver, get_driver
from vector.wiki_indexer import index_all_wiki


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ─── 시작 ────────────────────────────────────────────────────────────────
    # Neo4j 연결 시도 (실패해도 앱 정상 구동)
    await init_driver()

    # wiki_data/ → ChromaDB 인덱싱
    count = index_all_wiki()
    if count > 0:
        print(f"[Wiki] {count}개 문서 인덱싱 완료")

    yield

    # ─── 종료 ────────────────────────────────────────────────────────────────
    await close_driver()


app = FastAPI(
    title="제조 현장 AI 에이전트 API",
    description="철강/열연 공장 인텔리전스 플랫폼 — PydanticAI 에이전트 백엔드",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/agent/run")
async def agent_run(request: AgentRunRequest):
    """
    시나리오를 실행하고 RichRenderer가 소비할 구조화된 결과를 반환합니다.

    - S1, S2: 시뮬레이터 에이전트
    - S3, S5, S7: 트레이서 에이전트
    - S4, S6: RAG 에이전트
    """
    try:
        result = await run_scenario(request)
        # Pydantic 모델 → dict 직렬화 (한국어 키 포함)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"에이전트 실행 오류: {str(e)}")


@app.get("/health")
async def health():
    """서버 상태 및 연결된 인프라 확인."""
    from vector.chroma_client import get_collection
    return {
        "status": "ok",
        "neo4j": "connected" if get_driver() else "mock",
        "chromadb": "connected" if get_collection() else "unavailable",
    }
