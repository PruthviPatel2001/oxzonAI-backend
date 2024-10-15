from flask import  jsonify
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from huggingface_hub import InferenceClient
from services.queryDocument import post_process_answer
from dotenv import load_dotenv

load_dotenv()

def summarize_large_document(document):
    """Handles summarization requests for a PDF document."""
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

        summaries = {
            "abstractive": [],
            "extractive": []
        }

        try:
            client = InferenceClient(api_key=os.getenv("LLM_API_KEY")) 
            
            # Generate abstractive summaries
            for doc in texts:
                if hasattr(doc, 'page_content'):
                    input_text = doc.page_content
                else:
                    raise ValueError(f"Unexpected type for document: {type(doc)}")

                # Generate abstractive summary
                messages_abstractive = [
                    {"role": "user", "content": f"Please provide an abstractive summary for the following text:\n\n{input_text}"}
                ]
                summary_candidate_abstractive = ""
                
                for message in client.chat_completion(
                    model="meta-llama/Llama-3.2-1B-Instruct",
                    messages=messages_abstractive,
                    max_tokens=500,
                    stream=True,
                    temperature=0.7,
                ):
                    summary_candidate_abstractive += " " + message.choices[0].delta.content.strip()

                # Post-process the summary
                formatted_summary_abstractive = post_process_answer(summary_candidate_abstractive)
                summaries["abstractive"].append(formatted_summary_abstractive)

            # Generate extractive summaries
            for doc in texts:
                if hasattr(doc, 'page_content'):
                    input_text = doc.page_content
                else:
                    raise ValueError(f"Unexpected type for document: {type(doc)}")

                # Generate extractive summary
                messages_extractive = [
                    {"role": "user", "content": f"Please provide an extractive summary for the following text:\n\n{input_text}"}
                ]
                summary_candidate_extractive = ""

                for message in client.chat_completion(
                    model="meta-llama/Llama-3.2-1B-Instruct",
                    messages=messages_extractive,
                    max_tokens=500,
                    stream=True,
                    temperature=0.7,
                ):
                    summary_candidate_extractive += " " + message.choices[0].delta.content.strip()

                # Post-process the summary
                formatted_summary_extractive = post_process_answer(summary_candidate_extractive)
                summaries["extractive"].append(formatted_summary_extractive)

            # Combine the summaries for both types
            overall_summary_abstractive = combine_summaries(summaries["abstractive"])
            overall_summary_extractive = combine_summaries(summaries["extractive"])

            if not overall_summary_abstractive.strip() and not overall_summary_extractive.strip():
                return jsonify({'error': 'No summary could be generated.'}), 404

        except Exception as e:
            print(e)
            return jsonify({'error': f'Error generating summary: {str(e)}'}), 500

        return jsonify({
            'summaries': {
                'abstractive': overall_summary_abstractive,
                'extractive': overall_summary_extractive
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

def combine_summaries(summaries):
    """Combine individual summaries into a single summary."""
    return "\n".join(summaries)
