from flask import request, jsonify
from db import mongo  
from bson.objectid import ObjectId
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from huggingface_hub import InferenceClient
# import env 
from dotenv import load_dotenv

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
        
        file_path = document['pdf_location']

        # Load the document
        try:
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
        except Exception as e:
            return jsonify({'error': f'Error loading document: {str(e)}'}), 500

        # Split the document into manageable pieces
        try:
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)
        except Exception as e:
            return jsonify({'error': f'Error splitting document: {str(e)}'}), 500

        answer = None

        try:
            client = InferenceClient(api_key=os.getenv("LLM_API_KEY")) 
            for doc in texts:
                # Access the text content
                if hasattr(doc, 'page_content'):
                    input_text = doc.page_content
                else:
                    raise ValueError(f"Unexpected type for document: {type(doc)}")

                messages = [
                    {"role": "user", "content": f"Here is some context from a document:\n\n{input_text}\n\nBased on this context, please answer the following question: {user_query}"}
                ]

                answer_candidate = ""
                for message in client.chat_completion(
                    model="meta-llama/Llama-3.2-1B-Instruct",
                    messages=messages,
                    max_tokens=1000,
                    stream=True,
                    temperature=0.7,  # Adjust the temperature
                ):
                    answer_candidate += " "+ message.choices[0].delta.content.strip()

                formatted_answer = post_process_answer(answer_candidate)

                if answer is None or len(formatted_answer) > len(answer):
                    answer = formatted_answer

            if answer is None or answer.strip() == "":
                return jsonify({'error': 'No answer found for the provided question.'}), 404

        except Exception as e:
            return jsonify({'error': f'Error generating answer: {str(e)}'}), 500

        return jsonify({'answer': answer}), 200

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
   