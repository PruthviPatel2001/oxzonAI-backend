import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the embedding model (you can load this globally for efficiency)
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')

def generate_embedding(text):
    """Generate embedding for the given text using Sentence Transformers."""
    try:
        # Generate embedding for the document text
        embedding = embedding_model.encode(text)
        
        # Convert embedding to NumPy array with float32 type for FAISS
        if isinstance(embedding, np.ndarray):
            embedding_faiss = embedding.astype(np.float32)  # Ensure correct format for FAISS
        else:
            embedding_faiss = np.array(embedding, dtype=np.float32)
        
        # Convert embedding to list for MongoDB storage
        embedding_mongo = embedding_faiss.tolist()  # Convert to list for MongoDB

        # Return both formats: one for FAISS (NumPy array) and one for MongoDB (list)
        return embedding_faiss, embedding_mongo

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None, None

