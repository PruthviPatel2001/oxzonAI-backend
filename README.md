# AI-Based Knowledge-Based Search Retrieval System - Backend

## Overview

This repository contains the backend code for the AI-Based Knowledge-Based Search Retrieval System. The backend is built using Flask and integrates with MongoDB Atlas to provide a robust database solution. The application utilizes a Large Language Model (LLM) to handle complex queries efficiently, facilitating a seamless experience for users.

## Features

- **Flask-based API**: A RESTful API built using Flask for efficient data handling.
- **MongoDB Atlas Integration**: Utilizes MongoDB Atlas for cloud-based data storage.
- **Large Language Model**: Leverages the `meta-llama/Llama-3.2-1B-Instruct` model from Hugging Face to process user queries.
- **Partial RAG Architecture**: A partial implementation of the RAG (Retrieval-Augmented Generation) architecture is available in the `improving-architecture` branch. Full implementation is yet to be completed.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)

## Technologies

This project utilizes the following technologies:

- **Flask**: A lightweight WSGI web application framework in Python.
- **Flask-CORS**: A Flask extension for handling Cross-Origin Resource Sharing (CORS).
- **Flask-PyMongo**: A Flask extension that simplifies the use of PyMongo with Flask.
- **MongoDB Atlas**: A cloud-based database service for MongoDB.
- **Hugging Face Transformers**: A library for natural language processing tasks.
- **Langchain**: A framework for developing applications powered by language models.
- **PyMuPDF**: A library for reading and manipulating PDF files.

## Project Setup

### Clone the Repository

```bash
git clone <repository-url>
```

### Setup server

1. Go to Folder.

```bash
cd <folder-name>
```

2. Installs required packages for the backend.

```bash
pip install -r requirements.txt
```

3. Create a .env File.

```bash
LLM_API_KEY=your_llm_api_key_here

MONGODB_URI=your_mongodb_uri_here
```

4. Run application

```bash
python3 app.py
```

### Environment Variables

- LLM_API_KEY: Your API key for accessing the LLM from Hugging Face.
- MONGODB_URI: The connection string for your MongoDB Atlas database.

  **Create an LLM Access Token**:
  To use the LLM model from Hugging Face, you need to create an access token. You can do this by visiting [Hugging Face Tokens Settings](https://huggingface.co/settings/tokens).

## Note on RAG Architecture and Vector Database

The implementation of the RAG (Retrieval-Augmented Generation) architecture and Vector Database is still in progress. You can find a partial implementation in the `improving-architecture` branch.

## LLM Model

This project uses the LLM model from Hugging Face: [meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct).
