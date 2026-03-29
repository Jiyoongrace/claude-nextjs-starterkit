# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 명령어

```bash
npm run dev        # Turbopack 개발 서버
npm run build      # Turbopack 프로덕션 빌드
npm run start      # 프로덕션 서버 실행
npm run lint       # ESLint 실행
```

테스트 프레임워크는 설정되어 있지 않음.

## 기술 스택

- **Next.js 15** (App Router, Turbopack)
- **React 19**, **TypeScript 5** (strict mode, path alias `@/*` → `./src/*`)
- **TailwindCSS v4** — `tailwind.config.js` 없음, CSS-first 방식 (`src/app/globals.css`에서 설정)
- **shadcn/ui** (`base-nova` 스타일) + **@base-ui/react** (headless primitives)
- **next-themes** — 다크모드

## 시스템 개요

철강/열연 공장을 위한 **AI 에이전트 백본 플랫폼** (`/platform` 경로).
3종류 에이전트(시뮬레이터·트레이서·RAG)를 오케스트레이션하는 UI.

## 아키텍처

### 라우팅 구조

```
/ → redirect → /platform
/platform         → src/app/platform/ (3단 에이전트 레이아웃)
/api/agent/run    → POST: 시나리오 실행 (mock-agents.ts 호출)
/api/chat         → POST: Claude API 코파일럿 채팅
/api/files        → GET: wiki_data/ 파일 트리
/api/files/[...path] → GET/POST: 파일 읽기·쓰기
```

### 상태 관리

`WorkspaceContext` (`src/lib/workspace-context.tsx`)가 전체 UI 상태를 관리:
- `mode`: 4가지 워크스페이스 모드 (home / scenario / result / document)
- `copilotOpen`: 우측 코파일럿 패널 열림 여부
- `setMode()`로 사이드바·버튼 등 모든 네비게이션 처리

### 3단 레이아웃 (`src/app/platform/layout.tsx`)

```
┌──────────────────┬──────────────────────────┬──────────────┐
│ Sidebar (w-60)   │ main (flex-1)            │ CopilotPanel │
│ 시나리오 런처    │ mode에 따라 컴포넌트 교체 │ (w-80, 조건부)│
│ + 파일 트리      │                          │              │
└──────────────────┴──────────────────────────┴──────────────┘
```

중앙 패널은 `platform/page.tsx`에서 `mode` 값에 따라 컴포넌트를 switch:
- `home` → `HomeDashboard`
- `scenario` → `ScenarioPanel`
- `result` → `ResultPanel` + `RichRenderer`
- `document` → `Workspace` (마크다운 뷰어/에디터 + MetadataPanel)

### RichRenderer (`src/components/agent/RichRenderer/`)

에이전트 응답 `type`에 따라 6가지 렌더러로 분기:

| type | 렌더러 | 주요 라이브러리 |
|---|---|---|
| `simulation_table` | SimulationTable | 기본 테이블 |
| `ripple_effect` | RippleEffect | mermaid + recharts |
| `git_timeline` | GitTimeline | 커스텀 타임라인 UI |
| `graph_path` | GraphPath | reactflow |
| `wiki_result` | WikiResult | react-markdown + remark-gfm |
| `msa_diff` | MsaDiff | 좌우 비교 테이블 |

### Mock 에이전트 교체 포인트

`src/lib/mock-agents.ts`의 각 `if (scenarioId === "SN")` 블록이
추후 실제 에이전트(PydanticAI Tool, Neo4j 쿼리, Git 파싱)로 1:1 교체됩니다.

### Wiki 파일 시스템

`wiki_data/` (프로젝트 루트) — YAML 프론트매터 포함 마크다운 파일.
`연관_시나리오`와 `담당_에이전트` 필드가 추후 Graph DB 노드 연결에 활용됩니다.
`MetadataPanel`에서 편집 후 `gray-matter`로 프론트매터를 읽고 씁니다.

### 컴포넌트 레이어

1. `src/components/ui/` — shadcn/ui 기반 컴포넌트 (copy-paste 방식)
2. `cn()` (`src/lib/utils.ts`) — `clsx` + `tailwind-merge`
3. `SCENARIOS` 상수 (`src/lib/scenarios.ts`) — 7개 시나리오 메타데이터 단일 소스

### 스타일링 규칙

- TailwindCSS v4 CSS-first — `tailwind.config.js` 생성 금지
- 공통 입력 스타일: `input-field` 클래스 (`globals.css`에 정의)
- 다크모드: `.dark:` 변형 사용
- `<html suppressHydrationWarning>` 필수 유지 (next-themes)
- 인터랙티브 컴포넌트는 반드시 `"use client"` 선언

### 추가 설치된 패키지

```
@uiw/react-md-editor  — 마크다운 에디터 (SSR 비활성화 필요: dynamic import)
react-markdown        — 마크다운 렌더링
remark-gfm           — GFM 확장
mermaid              — 다이어그램 (dynamic import, 클라이언트 전용)
reactflow            — 온톨로지 그래프 시각화
recharts             — 시계열 차트
gray-matter          — YAML 프론트매터 파싱
@anthropic-ai/sdk    — Claude API (api/chat/route.ts에서 사용)
```

---

## 백엔드 및 AI 에이전트 스택 (Agent Backend)

> 이 섹션은 Next.js 프론트엔드와 분리된 **Python 백엔드 + AI 에이전트 레이어**에 대한
> 기술 스택 및 아키텍처 가이드입니다.
> 백엔드는 `/backend` 디렉토리에서 독립적으로 실행됩니다.

### 디렉토리 구조
```
backend/
├── main.py                        # FastAPI 앱 진입점
├── pyproject.toml                 # 의존성 관리 (uv 권장)
├── .env                           # 환경변수 (API 키 등)
├── agents/
│   ├── orchestrator.py            # 메인 오케스트레이터 에이전트
│   ├── simulator_agent.py         # 🔮 Role 2: 시뮬레이터 에이전트
│   ├── tracer_agent.py            # 🔍 Role 3: 트레이서 에이전트
│   └── rag_agent.py               # 📚 RAG 에이전트 (용어/Runbook)
├── tools/
│   ├── simulation_tools.py        # 시뮬레이션 Tool 함수들
│   ├── graph_tools.py             # Neo4j 탐색 Tool 함수들
│   ├── git_tools.py               # Git 이력 파싱 Tool 함수들
│   ├── db_tools.py                # DB 조회 Tool 함수들 (Mock 우선)
│   └── wiki_tools.py              # Wiki 파일 읽기/쓰기 Tool 함수들
├── models/
│   ├── request_models.py          # Pydantic 요청 스키마
│   └── response_models.py         # Pydantic 응답 스키마 (RichRenderer 타입과 1:1 대응)
├── graph/
│   ├── neo4j_client.py            # Neo4j 드라이버 연결
│   └── ontology_loader.py         # 온톨로지 초기 데이터 로딩
├── vector/
│   ├── chroma_client.py           # ChromaDB 클라이언트
│   └── wiki_indexer.py            # wiki_data 마크다운 → 벡터 인덱싱
└── wiki_data/                     # Docsify 마크다운 파일 (프론트와 공유)
```

---

### 기술 스택 및 선택 근거

#### 1. 백엔드 프레임워크: FastAPI
```bash
pip install fastapi uvicorn
```

**선택 근거:**
- PydanticAI와 동일한 Pydantic 생태계 → 요청/응답 스키마를 에이전트 출력과 직접 공유 가능
- 비동기(async) 기반으로 LLM 스트리밍 응답과 자연스럽게 연동
- Next.js → FastAPI 간 REST API 통신 구조가 명확하고 단순
```python
# main.py 기본 구조
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SCM Ops Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### 2. AI 에이전트 프레임워크: PydanticAI
```bash
pip install pydantic-ai
```

**선택 근거 (vs LangChain/LangGraph):**
- LangChain/LangGraph: 러닝커브가 길고, 중간에 구조를 뜯어고쳐야 하는 상황이 자주 발생
- PydanticAI: Tool 정의 → 에이전트 실행 → 구조화된 JSON 출력까지 코드량이 최소화됨
- `@agent.tool` 데코레이터로 Mock 함수를 실제 함수로 1:1 교체 가능 → 데모 후 확장 용이
```python
# agents/simulator_agent.py 기본 구조 예시
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from models.response_models import SimulationResult

simulator_agent = Agent(
    model=AnthropicModel("claude-sonnet-4-20250514"),
    result_type=SimulationResult,          # Pydantic 모델로 출력 타입 강제
    system_prompt="""
    당신은 제조 공정 시뮬레이션 전문 AI 에이전트입니다.
    DG320 에러 방지를 위한 최적 파라미터를 탐색하고,
    Edging 기준 변경에 따른 후공정 파급 효과를 분석합니다.
    반드시 도구(Tool)를 사용하여 가설을 검증하세요.
    """,
)

@simulator_agent.tool
async def run_simulation(width: float, thickness: float) -> dict:
    """
    ⚠️ Mock 함수 — 추후 실제 시뮬레이터 Python 로직으로 교체
    주어진 폭/두께 파라미터로 DG320 위험도를 계산합니다.
    """
    # Mock 계산 로직 (선형 근사)
    risk = max(0, min(100, (width - 1000) * 0.15 + (9.0 - thickness) * 20))
    return {
        "width": width,
        "thickness": thickness,
        "dg320_risk_percent": round(risk, 1),
        "status": "위험" if risk > 70 else "경고" if risk > 30 else "안전",
    }
```

---

#### 3. 그래프 DB: Neo4j (온톨로지 저장소)
```bash
pip install neo4j
```

**선택 근거:**
- 시스템 간 데이터 흐름(MSA), 코드-DB-화면 간 의미적 관계를 그래프로 모델링하는 데 최적
- Cypher 쿼리로 "이 에러코드 → 어떤 DB 테이블 → 어떤 서비스 → 어떤 화면" 경로 탐색 가능
- Neo4j AuraDB 무료 클라우드 티어로 로컬 설치 없이 즉시 시작 가능

**온톨로지 노드 설계 (데모 범위):**
```
(:ErrorCode {id: "DG320", description: "단중 초과 에러"})
(:DBTable  {id: "TB_SLAB_TARGET", columns: ["slab_id", "target_weight"]})
(:Service  {id: "PlanningAPI", endpoint: "/api/slab/plan"})
(:Screen   {id: "SCR_QUALITY_MGR", name: "품질관리 화면"})
(:GitCommit {hash: "b71e4d8", message: "단중 허용 범위 상수값 변경"})

(DG320)-[:CAUSED_BY]->(TB_SLAB_TARGET)
(TB_SLAB_TARGET)-[:QUERIED_BY]->(PlanningAPI)
(PlanningAPI)-[:DISPLAYED_ON]->(SCR_QUALITY_MGR)
(TB_SLAB_TARGET)-[:CHANGED_BY]->(b71e4d8)
```

**DB 연동 대기 전략:**
> OT(운영 DB) 연동 승인이 날 때까지는 `graph/ontology_loader.py`에
> 위 노드/엣지 데이터를 하드코딩하여 Neo4j AuraDB에 초기 로딩합니다.
> 실제 DB 연동 시 loader만 교체하면 됩니다.
```python
# tools/graph_tools.py 기본 구조
from graph.neo4j_client import get_driver

async def traverse_error_path(error_code: str) -> list[dict]:
    """
    ⚠️ Mock 데이터 기반 — 추후 실제 Neo4j AuraDB 쿼리로 교체
    에러 코드에서 출발하여 원인 노드까지 경로를 탐색합니다.
    """
    driver = get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH path = (e:ErrorCode {id: $error_code})-[:CAUSED_BY*1..5]->(cause)
            RETURN nodes(path) AS nodes, relationships(path) AS rels
            """,
            error_code=error_code,
        )
        return [record.data() async for record in result]
```

---

#### 4. 벡터 DB: ChromaDB (Wiki RAG용)
```bash
pip install chromadb
```

**선택 근거 (vs Pinecone, Weaviate 등):**
- 로컬 파일 기반으로 동작 → 별도 서버 불필요, 해커톤 환경에 최적
- `wiki_data/` 마크다운 파일을 그대로 인덱싱 가능
- Docsify와 동일한 파일 시스템을 공유하므로 Wiki 업데이트 시 자동 재인덱싱 구현 용이
```python
# vector/wiki_indexer.py 기본 구조
import chromadb
from pathlib import Path

def index_wiki(wiki_dir: str = "wiki_data") -> None:
    """
    wiki_data/ 하위 모든 .md 파일을 ChromaDB에 인덱싱합니다.
    Wiki 파일이 업데이트될 때마다 호출하여 벡터를 갱신합니다.
    """
    client = chromadb.PersistentClient(path=".chromadb")
    collection = client.get_or_create_collection("wiki")

    for md_file in Path(wiki_dir).rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        collection.upsert(
            ids=[str(md_file)],
            documents=[content],
            metadatas=[{"source": str(md_file)}],
        )
```

---

#### 5. Wiki 솔루션: Docsify

**선택 근거 (vs Wiki.js, BookStack 등):**
- 별도 빌드 없이 마크다운 파일만으로 즉시 렌더링 → 에이전트가 파일을 수정하면 실시간 반영
- 서버 사이드 DB 불필요 → `wiki_data/` 폴더를 FastAPI, ChromaDB, Next.js가 모두 공유
- `docsify-cli`로 로컬 서버 1줄 실행
```bash
npm install -g docsify-cli
docsify serve wiki_data --port 3001
```

> Docsify는 포트 3001에서 독립 실행합니다.
> Next.js(3000), FastAPI(8000), Docsify(3001) 세 서버가 동시에 동작합니다.

---

#### 6. 응답 스키마: Pydantic 모델 (프론트 RichRenderer와 1:1 대응)
```python
# models/response_models.py
from pydantic import BaseModel
from typing import Literal

class SimulationRow(BaseModel):
    시도: str
    폭: str
    두께: str
    DG320_위험도: str
    상태: str

class SimulationResult(BaseModel):
    type: Literal["simulation_table"]
    title: str
    params: dict[str, str]
    results: list[SimulationRow]
    optimal_index: int

class RippleEffectResult(BaseModel):
    type: Literal["ripple_effect"]
    title: str
    diagram: str                          # Mermaid 문법 문자열
    timeline: list[dict[str, str | int]]

class GitTimelineResult(BaseModel):
    type: Literal["git_timeline"]
    title: str
    commits: list[dict]

class GraphPathResult(BaseModel):
    type: Literal["graph_path"]
    title: str
    nodes: list[dict[str, str]]
    edges: list[dict[str, str]]

class WikiResult(BaseModel):
    type: Literal["wiki_result"]
    content: str
    mappings: list[dict[str, str]]

class MsaDiffResult(BaseModel):
    type: Literal["msa_diff"]
    title: str
    service_a: str
    service_b: str
    rows_a: list[dict[str, str]]
    rows_b: list[dict[str, str]]
    diff_keys: list[str]

# 유니온 타입 — FastAPI 응답 및 Next.js RichRenderer 타입과 동일 구조 유지
AgentResponse = (
    SimulationResult
    | RippleEffectResult
    | GitTimelineResult
    | GraphPathResult
    | WikiResult
    | MsaDiffResult
)
```

---

### 전체 아키텍처 흐름
```
사용자 (브라우저)
    │
    ▼
Next.js (포트 3000)                    Docsify (포트 3001)
    │  POST /api/agent/run                  │
    │  → Next.js Route Handler             Wiki 마크다운 렌더링
    │  → FastAPI 프록시                     (별도 탭 or 임베드)
    │
    ▼
FastAPI (포트 8000)
    │
    ├── POST /agent/run
    │       │
    │       ▼
    │   Orchestrator Agent (PydanticAI)
    │       │
    │       ├── 시나리오 S1, S2  →  Simulator Agent
    │       │                            └── @tool: run_simulation()
    │       │
    │       ├── 시나리오 S3, S5, S7  →  Tracer Agent
    │       │                            ├── @tool: traverse_graph()  → Neo4j AuraDB
    │       │                            ├── @tool: parse_git_log()
    │       │                            └── @tool: cross_check_db()  → Mock DB
    │       │
    │       └── 시나리오 S4, S6  →  RAG Agent
    │                                    └── @tool: search_wiki()  → ChromaDB
    │
    └── POST /chat
            └── Claude API (컨텍스트 주입 채팅)
```

---

### 개발 서버 실행 명령어
```bash
# 터미널 1 — Next.js 프론트엔드
npm run dev

# 터미널 2 — FastAPI 백엔드
cd backend
uvicorn main:app --reload --port 8000

# 터미널 3 — Docsify Wiki (선택)
docsify serve wiki_data --port 3001
```

---

### 환경변수 (.env)
```bash
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io   # AuraDB 무료 클라우드
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
CHROMA_PERSIST_DIR=.chromadb
WIKI_DATA_DIR=../wiki_data
```

---

### Mock → 실제 전환 포인트 (교체 우선순위)

| 우선순위 | 파일 | Mock 내용 | 교체 대상 |
|---|---|---|---|
| 1순위 | `tools/simulation_tools.py` | 선형 근사 계산 | 실제 공정 시뮬레이터 Python 함수 |
| 2순위 | `graph/ontology_loader.py` | 하드코딩 노드/엣지 | OT DB 연동 후 실제 스키마 파싱 |
| 3순위 | `tools/db_tools.py` | 하드코딩 Mock 테이블 | 실제 DB 쿼리 (OT 연동 승인 후) |
| 4순위 | `tools/git_tools.py` | 하드코딩 커밋 로그 | 실제 Git 레포 `git log` 파싱 |

> ⚠️ **OT DB 연동 대기 전략:**
> OT(운영 DB) 연동 승인 전까지는 `db_tools.py`의 Mock 함수로 전체 파이프라인을 완성합니다.
> 승인 후에는 해당 파일만 교체하면 나머지 에이전트 로직은 그대로 동작합니다.

---

### 주의사항 (에이전트 설계 원칙)

- **단순 챗봇 금지**: 에이전트는 반드시 Tool을 사용하여 정보를 조회/실행한 뒤 답변해야 합니다
- **Rule Base 금지**: if-else 분기로 답변을 하드코딩하지 마세요. 에이전트가 스스로 추론하여 Tool을 선택해야 합니다
- **ReAct 패턴 준수**: 가설 수립 → Tool 실행 → 결과 검증 → 재시도 루프를 PydanticAI의 다중 Tool 호출로 구현하세요
- **Guide + 실행 형태 유지**: 에이전트는 단순 안내(Guide)에 그치지 않고, 실제 Tool을 실행하여 구체적인 결과를 제시해야 합니다