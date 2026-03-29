"""
wiki_data/ 마크다운 파일 → ChromaDB 벡터 인덱서.
서버 시작 시 한 번 실행. Wiki 파일 수정 후 재호출하면 업서트 방식으로 갱신.
"""
import os
from pathlib import Path

try:
    import frontmatter
    _FRONTMATTER_AVAILABLE = True
except ImportError:
    _FRONTMATTER_AVAILABLE = False

from vector.chroma_client import get_collection

# backend/ 기준으로 wiki_data/ 경로 계산
_DEFAULT_WIKI_DIR = Path(__file__).parent.parent.parent / "wiki_data"


def index_all_wiki() -> int:
    """
    wiki_data/ 하위 모든 .md 파일을 ChromaDB에 업서트.
    반환값: 인덱싱된 파일 수 (ChromaDB 없으면 0)
    """
    collection = get_collection()
    if collection is None:
        print("[Wiki Indexer] ChromaDB 없음 → 인덱싱 건너뜀")
        return 0

    wiki_dir_env = os.getenv("WIKI_DATA_DIR", "")
    wiki_dir = Path(wiki_dir_env).resolve() if wiki_dir_env else _DEFAULT_WIKI_DIR

    if not wiki_dir.exists():
        print(f"[Wiki Indexer] wiki_data 디렉토리 없음: {wiki_dir}")
        return 0

    indexed = 0
    for md_file in wiki_dir.rglob("*.md"):
        try:
            if _FRONTMATTER_AVAILABLE:
                post = frontmatter.load(str(md_file))
                content = post.content
                meta = post.metadata
            else:
                content = md_file.read_text(encoding="utf-8")
                meta = {}

            collection.upsert(  # type: ignore
                ids=[str(md_file)],
                documents=[content],
                metadatas=[{
                    "source": str(md_file.relative_to(wiki_dir)),
                    "scenario": str(meta.get("연관_시나리오", [])),
                    "agent": str(meta.get("담당_에이전트", "")),
                    "tags": str(meta.get("비즈니스_태그", [])),
                }],
            )
            indexed += 1
        except Exception as e:
            print(f"[Wiki Indexer] 파일 인덱싱 실패 ({md_file.name}): {e}")

    return indexed


def search_wiki(query: str, n_results: int = 3) -> list[dict]:
    """
    자연어 쿼리로 wiki_data에서 관련 문서 검색.
    ChromaDB 없으면 빈 리스트 반환 → wiki_tools.py에서 Mock 폴백 처리.
    """
    collection = get_collection()
    if collection is None:
        return []

    try:
        results = collection.query(  # type: ignore
            query_texts=[query],
            n_results=n_results,
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"content": doc, "metadata": meta} for doc, meta in zip(docs, metas)]
    except Exception as e:
        print(f"[Wiki Indexer] 검색 실패: {e}")
        return []
