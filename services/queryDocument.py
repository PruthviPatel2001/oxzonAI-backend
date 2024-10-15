from flask import request, jsonify
from db import mongo  
from bson.objectid import ObjectId
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from huggingface_hub import InferenceClient
# import env 
from dotenv import load_dotenv

# from services.documentUpload import generate_embedding
from utils.generate_embedding import generate_embedding
from utils.setupForFAISS import add_embeddings_to_faiss, initialize_faiss_index, retrieve_similar_documents

load_dotenv()

def post_process_answer(answer_candidate):
    """Post-process the answer candidate to improve readability and format."""
   
    # Ensure proper spacing
    answer_candidate = ' '.join(answer_candidate.split())

    # Handle punctuation spacing
    answer_candidate = answer_candidate.replace('.', '. ').replace('?', '? ').replace('!', '! ').replace(" ,", ",")
    
    # Remove redundant spaces before punctuation
    answer_candidate = answer_candidate.replace("  ", " ")

    # Capitalize the first letter of the answer (if it's not empty)
    if answer_candidate:
        answer_candidate = answer_candidate[0].upper() + answer_candidate[1:]

    # Optionally: break long answers into paragraphs based on sentence length
    max_sentence_length = 100  
    sentences = answer_candidate.split('. ')
    formatted_answer = []
    
    current_paragraph = []
    for sentence in sentences:
        current_paragraph.append(sentence.strip())
        # Join sentences and check length
        if len('. '.join(current_paragraph)) > max_sentence_length:
            formatted_answer.append('. '.join(current_paragraph))
            current_paragraph = []
    
    # Append any remaining sentences
    if current_paragraph:
        formatted_answer.append('. '.join(current_paragraph))
    
    # Join paragraphs with double new lines for spacing
    return '\n\n'.join(formatted_answer)

def query_document_for_answer(user_query, document):
    try:
        # Initialize FAISS index
        faiss_index = initialize_faiss_index(dim=768)  # Assuming 768-dimensional embeddings
        
        # Get the document's embedding and store in FAISS index (assuming it's already added to FAISS)
        document_embeddings = mongo.db.DocumentEmbeddings.find({"document_id": document['_id']})
        
        # Add embeddings to FAISS index (assuming MongoDB stores document embeddings)
        embeddings = [embedding['embedding'] for embedding in document_embeddings]
        doc_ids = [str(embedding['document_id']) for embedding in document_embeddings]
        faiss_index = add_embeddings_to_faiss(faiss_index, embeddings, doc_ids)
        
        # Generate embedding for the user's query
        query_embedding = generate_embedding(user_query)
 
        # Retrieve similar documents using FAISS
        similar_docs, distances = retrieve_similar_documents(faiss_index, query_embedding, k=5)
        
        # Initialize LangChain's document loader and text splitter for document processing
        context = ""
        for doc_id in similar_docs:
            doc = mongo.db.ReportDetails.find_one({"_id": ObjectId(doc_id)})
            if doc and 'pdf_location' in doc:
                file_path = doc['pdf_location']

                try:
                    # Load the document using LangChain
                    loader = PyMuPDFLoader(file_path)
                    documents = loader.load()

                    # Split the document into chunks (text splitting)
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    texts = text_splitter.split_documents(documents)

                    # Combine chunks to form context for the LLM
                    for text in texts:
                        context += text.page_content  # Assuming text contains 'page_content'
                except Exception as e:
                    return jsonify({'error': f'Error processing document: {str(e)}'}), 500
        
        # If no context is found, return an error
        if not context:
            return jsonify({'error': 'No relevant context found from documents.'}), 404

        # Generate an answer using the LLM with the retrieved context
        client = InferenceClient(api_key=os.getenv("LLM_API_KEY"))
        
        messages = [
            {"role": "user", "content": f"Here is some context from a document:\n\n{context}\n\nBased on this context, please answer the following question: {user_query}"}
        ]
        
        answer_candidate = ""
        for message in client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",  # Choose an appropriate model
            messages=messages,
            max_tokens=1000,
            stream=True,
            temperature=0.7,  # Adjust the temperature
        ):
            answer_candidate += " " + message.choices[0].delta.content.strip()

        # Post-process the answer
        formatted_answer = post_process_answer(answer_candidate)

        if formatted_answer is None or formatted_answer.strip() == "":
            return jsonify({'error': 'No answer found for the provided question.'}), 404

        return jsonify({'answer': formatted_answer}), 200

    except Exception as e:
        return jsonify({'error': f'Error generating answer: {str(e)}'}), 500