import faiss
import numpy as np

# Initialize FAISS index
def initialize_faiss_index(dim=768):
    """Initialize a FAISS index."""
    try:
        index = faiss.IndexFlatL2(dim)  # Flat L2 distance index
        if not index.is_trained:
            raise Exception("FAISS index is not trained.")
        return index
    except Exception as e:
        print(f"Error initializing FAISS index: {e}")
        return None

# Add embeddings to FAISS index
def add_embeddings_to_faiss(index, embeddings, doc_ids):
    """Add embeddings to the FAISS index."""
    try:
        embeddings = np.array(embeddings).astype(np.float32)  # Ensure embeddings are float32
        doc_ids = np.array(doc_ids, dtype=np.int64)  # FAISS requires int64 for IDs
        index.add_with_ids(embeddings, doc_ids)
    except Exception as e:
        print(f"Error adding embeddings to FAISS: {e}")


# Retrieve similar documents from FAISS
def retrieve_similar_documents(index, query_embedding, k=5):
    query_embedding = np.array(query_embedding).astype(np.float32).reshape(1, -1)
    distances, indices = index.search(query_embedding, k)
    return indices, distances