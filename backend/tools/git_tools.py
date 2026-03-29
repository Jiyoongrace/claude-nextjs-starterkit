"""
Git 이력 파싱 Tool 함수 — S3 담당.

⚠️ 교체 포인트 (Phase 4):
    parse_git_log() → subprocess로 실제 Git 레포 `git log` 파싱으로 교체
"""

# ─── Mock 데이터 (mock-agents.ts S3 데이터와 동일) ──────────────────────────
_MOCK_COMMITS = [
    {
        "hash": "a3f9c21",
        "message": "feat: Slab 두께 계산 로직 수정",
        "author": "kim.dev",
        "date": "2025-03-24 09:12",
        "is_suspect": False,
    },
    {
        "hash": "b71e4d8",
        "message": "fix: 단중 허용 범위 상수값 변경 (320→295)",
        "author": "lee.dev",
        "date": "2025-03-25 14:33",
        "is_suspect": True,   # 의심 커밋 — 빨간 하이라이트
    },
    {
        "hash": "c90a1f3",
        "message": "refactor: Job 스케줄러 타임아웃 조정",
        "author": "park.dev",
        "date": "2025-03-25 17:55",
        "is_suspect": False,
    },
    {
        "hash": "d44b2e7",
        "message": "hotfix: NPE 방지 null 체크 추가",
        "author": "kim.dev",
        "date": "2025-03-26 08:01",
        "is_suspect": False,
    },
]


async def parse_git_log(job_id: str, date_from: str, date_to: str) -> list[dict]:
    """
    지정 Job ID 관련 커밋 이력을 파싱하고 의심 커밋을 탐지합니다.

    ⚠️ Mock 구현 — 하드코딩 커밋 로그
    교체 대상:
        import subprocess
        result = subprocess.run(
            ["git", "log", f"--since={date_from}", f"--until={date_to}",
             "--pretty=format:%H|%s|%an|%ai"],
            capture_output=True, text=True, cwd="/path/to/repo"
        )
        # 파싱 후 is_suspect 판별 로직 추가
    """
    return _MOCK_COMMITS


async def detect_suspect_commits(commits: list[dict]) -> list[dict]:
    """
    커밋 목록에서 의심 패턴을 탐지하여 is_suspect 플래그를 설정합니다.

    탐지 기준 (Mock):
    - 메시지에 "상수값 변경", "허용 범위" 등 임계값 변경 키워드 포함
    - 비정상 종료 시각과 근접한 커밋
    """
    SUSPECT_KEYWORDS = ["상수값 변경", "허용 범위", "임계값", "limit", "threshold"]
    for commit in commits:
        msg = commit.get("message", "").lower()
        commit["is_suspect"] = any(kw in msg for kw in SUSPECT_KEYWORDS)
    return commits
