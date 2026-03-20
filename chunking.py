from typing import List
from docling_core.types.doc.document import DoclingDocument

from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

chunker = HybridChunker()

def chunk(doc: DoclingDocument) -> List[str]: 
    chunk_iter = chunker.chunk(dl_doc=doc)

    chunks = []

    for chunk in chunk_iter:
        contextualized_text = chunker.contextualize(chunk=chunk)
        chunks.append(contextualized_text)

    return chunks

def batch_chunks(chunks: List[str], batch_size: int=5):
    """
    Agrupa chunks em lotes para evitar uma chamada de IA por chunk.
    """
    for i in range(0, len(chunks), batch_size):
        yield chunks[i:i + batch_size]
