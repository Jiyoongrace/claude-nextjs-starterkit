import os
from typing import Optional

try:
    import chromadb
    from chromadb import Collection
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
    Collection = None  # type: ignore

_collection: Optional[object] = None


def get_collection() -> Optional[object]:
    """
    ChromaDB 컬렉션 반환.
    None이면 chromadb 미설치 또는 초기화 실패 — wiki_tools.py에서 Mock 폴백 처리.
    """
    global _collection
    if _collection is not None:
        return _collection

    if not _CHROMA_AVAILABLE:
        return None

    try:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", ".chromadb")
        client = chromadb.PersistentClient(path=persist_dir)
        _collection = client.get_or_create_collection(
            "wiki",
            metadata={"hnsw:space": "cosine"},
        )
        return _collection
    except Exception as e:
        print(f"[ChromaDB] 초기화 실패 → Mock 폴백: {e}")
        return None
