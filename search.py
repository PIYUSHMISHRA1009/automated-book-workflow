from ai.embeddings import search_similar_chapters

def search_chapters(query: str):
    """
    Perform semantic search and format results for frontend display.
    """
    raw = search_similar_chapters(query)

    # Check if results are valid
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]

    # Format combined output
    results = []
    for doc, meta in zip(documents, metadatas):
        chapter = meta.get("chapter", "N/A")
        title = meta.get("title", "Untitled")
        score = meta.get("score", 0)
        snippet = doc[:400] + "..." if len(doc) > 400 else doc
        result_text = f"📘 Chapter {chapter}: {title}\n🔍 Score: {score:.2f}\n\n{snippet}"
        results.append(result_text)

    return results
