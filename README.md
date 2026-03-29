# 제조 현장 AI 에이전트 인텔리전스 플랫폼

철강/열연 공장을 위한 **AI 에이전트 백본 플랫폼**입니다.
시뮬레이터·트레이서·RAG 3종류 에이전트를 오케스트레이션하는 UI와
FastAPI + PydanticAI 기반의 실행 백엔드로 구성됩니다.

---

## 기술 스택

### 프론트엔드
| 항목 | 버전/내용 |
|---|---|
| Next.js | 15 (App Router, Turbopack) |
| React | 19 |
| TypeScript | 5 (strict mode) |
| TailwindCSS | v4 (CSS-first, config 파일 없음) |
| shadcn/ui | base-nova 스타일 |
| @base-ui/react | headless primitives |
| next-themes | 다크모드 지원 |

### 백엔드
| 항목 | 버전/내용 |
|---|---|
| Python | 3.11+ |
| FastAPI | 0.115+ |
| PydanticAI | 0.0.15+ (ReAct 패턴 에이전트) |
| Pydantic | v2 |
| Neo4j | 5.27+ (온톨로지 그래프 DB) |
| ChromaDB | 0.6+ (Wiki RAG 벡터 DB) |
| uvicorn | ASGI 서버 |
| uv | 패키지 관리자 (권장) |

### AI / LLM
| 항목 | 용도 |
|---|---|
| Anthropic Claude (PydanticAI) | 백엔드 에이전트 추론 |
| Groq API (llama-3.3-70b) | 프론트엔드 코파일럿 채팅 |

### 시각화 라이브러리
| 라이브러리 | 용도 |
|---|---|
| reactflow | 온톨로지 그래프 시각화 |
| recharts | 시계열 차트 |
| mermaid | 파급 효과 다이어그램 |
| react-markdown + remark-gfm | Wiki 마크다운 렌더링 |
| @uiw/react-md-editor | 마크다운 에디터 |

---

## 프로젝트 구조

```
.
├── src/
│   ├── app/
│   │   ├── platform/              # 메인 플랫폼 UI
│   │   │   ├── layout.tsx         # 3단 레이아웃 (사이드바 + 메인 + 코파일럿)
│   │   │   └── page.tsx           # mode 스위치 라우터
│   │   └── api/
│   │       ├── agent/run/         # POST: FastAPI 에이전트 프록시
│   │       ├── chat/              # POST: Groq 코파일럿 채팅
│   │       ├── files/             # GET: Wiki 파일 트리
│   │       └── files/[...path]/   # GET/POST: 파일 읽기·쓰기
│   ├── components/
│   │   ├── agent/
│   │   │   ├── RichRenderer/      # 6종 응답 렌더러 (타입 기반 분기)
│   │   │   ├── ScenarioPanel.tsx  # 시나리오 실행 UI
│   │   │   ├── ResultPanel.tsx    # 에이전트 결과 패널
│   │   │   └── HomeDashboard.tsx  # 홈 대시보드
│   │   └── ui/                    # shadcn/ui 컴포넌트
│   └── lib/
│       ├── workspace-context.tsx  # 전역 UI 상태 관리
│       ├── scenarios.ts           # 7개 시나리오 메타데이터
│       └── utils.ts               # cn() 유틸리티
│
├── backend/
│   ├── main.py                    # FastAPI 진입점
│   ├── pyproject.toml             # 의존성 (uv 관리)
│   ├── agents/
│   │   ├── orchestrator.py        # 시나리오 ID → 에이전트 라우팅
│   │   ├── simulator_agent.py     # S1·S2: 공정 시뮬레이션
│   │   ├── tracer_agent.py        # S3·S5·S7: 그래프 추적
│   │   └── rag_agent.py           # S4·S6: Wiki RAG 검색
│   ├── tools/
│   │   ├── simulation_tools.py    # 시뮬레이션 Tool 함수
│   │   ├── graph_tools.py         # Neo4j 탐색 Tool 함수
│   │   ├── git_tools.py           # Git 이력 파싱 Tool 함수
│   │   ├── db_tools.py            # DB 조회 Tool 함수 (Mock)
│   │   └── wiki_tools.py          # Wiki 읽기·쓰기 Tool 함수
│   ├── models/
│   │   ├── request_models.py      # AgentRunRequest 스키마
│   │   └── response_models.py     # RichRenderer 타입과 1:1 대응 응답 스키마
│   ├── graph/
│   │   ├── neo4j_client.py        # Neo4j 드라이버
│   │   └── ontology_loader.py     # 온톨로지 초기 데이터 로딩
│   └── vector/
│       ├── chroma_client.py       # ChromaDB 클라이언트
│       └── wiki_indexer.py        # wiki_data → 벡터 인덱싱
│
└── wiki_data/                     # Docsify 마크다운 문서
```

---

## 아키텍처 흐름

```
사용자 (브라우저)
    │
    ▼
Next.js (:3000)                        Docsify (:3001)
    │  POST /api/agent/run               Wiki 문서 렌더링
    │  → FastAPI 프록시
    │
    ▼
FastAPI (:8000)  POST /agent/run
    │
    └── Orchestrator
            ├── S1, S2  →  Simulator Agent  → run_simulation()
            ├── S3, S5, S7  →  Tracer Agent → traverse_graph() / parse_git_log()
            └── S4, S6  →  RAG Agent        → search_wiki() → ChromaDB
```

### RichRenderer — 응답 타입별 시각화

| type | 렌더러 | 시각화 |
|---|---|---|
| `simulation_table` | SimulationTable | 파라미터 비교 테이블 |
| `ripple_effect` | RippleEffect | Mermaid 다이어그램 + Recharts |
| `git_timeline` | GitTimeline | 커밋 타임라인 |
| `graph_path` | GraphPath | ReactFlow 노드 그래프 |
| `wiki_result` | WikiResult | 마크다운 + 매핑 테이블 |
| `msa_diff` | MsaDiff | MSA 간 데이터 비교 |

### 7개 시나리오

| ID | 에이전트 | 내용 |
|---|---|---|
| S1 | Simulator | DG320 에러 방지 최적 파라미터 탐색 |
| S2 | Simulator | Edging 기준 변경 파급 효과 분석 |
| S3 | Tracer | Job 비정상 종료 원인 추적 |
| S4 | RAG | 용어 정의 및 화면/DB/API 매핑 조회 |
| S5 | Tracer | 신규 공장 신설 영향 컴포넌트 탐색 |
| S6 | RAG | 권한 신청 결재 초안 런북 기반 생성 |
| S7 | Tracer | MSA 간 데이터 불일치 탐지 |

---

## 개발 서버 실행

```bash
# 터미널 1 — Next.js 프론트엔드 (포트 3000)
npm run dev

# 터미널 2 — FastAPI 백엔드 (포트 8000)
cd backend
uv run uvicorn main:app --reload --port 8000

# 터미널 3 — Docsify Wiki (포트 3001, 선택)
docsify serve wiki_data --port 3001
```

---

## 환경변수 설정

**`backend/.env`**
```bash
ANTHROPIC_API_KEY=sk-ant-...

# Neo4j AuraDB (무료 클라우드 티어)
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...

CHROMA_PERSIST_DIR=.chromadb
WIKI_DATA_DIR=../wiki_data
```

**`.env.local`** (Next.js)
```bash
GROQ_API_KEY=gsk_...
GROQ_CHAT_MODEL=llama-3.3-70b-versatile   # 생략 시 기본값
```

---

## 백엔드 의존성 설치

```bash
cd backend

# uv 사용 (권장)
uv sync

# 또는 pip
pip install -e .
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/agent/run` | 시나리오 실행 → RichRenderer 응답 |
| `GET` | `/health` | 서버 상태 및 Neo4j·ChromaDB 연결 확인 |

### 요청 예시

```json
POST /agent/run
{
  "scenario_id": "S1",
  "params": {
    "width": 1200,
    "thickness": 8.5,
    "error_code": "DG320"
  }
}
```

---

## Mock → 실제 전환 포인트

| 우선순위 | 파일 | 교체 대상 |
|---|---|---|
| 1 | `tools/simulation_tools.py` | 실제 공정 시뮬레이터 Python 함수 |
| 2 | `graph/ontology_loader.py` | OT DB 연동 후 실제 스키마 파싱 |
| 3 | `tools/db_tools.py` | 실제 DB 쿼리 (OT 연동 승인 후) |
| 4 | `tools/git_tools.py` | 실제 Git 레포 `git log` 파싱 |

> 각 Tool 함수는 `@agent.tool` 데코레이터로 에이전트에 주입되므로,
> Mock 함수를 실제 함수로 교체해도 에이전트 로직은 그대로 동작합니다.

---

## 주요 명령어

```bash
npm run dev        # Turbopack 개발 서버
npm run build      # Turbopack 프로덕션 빌드
npm run start      # 프로덕션 서버
npm run lint       # ESLint
```
