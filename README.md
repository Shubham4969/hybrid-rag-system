# Hybrid RAG System

A Python-based Retrieval-Augmented Generation (RAG) application designed to retrieve relevant information from documents and generate context-aware answers using Large Language Models (LLMs).

The project uses **Qdrant vector search, document chunking, embeddings, FastAPI, and background job processing with RQ**. Its roadmap includes hybrid BM25 retrieval and question answering across PDFs, videos, and Google Docs/Drive sources.

**Repository:** [Shubham4969/hybrid-rag-system](https://github.com/Shubham4969/hybrid-rag-system)

---

## Overview

Large Language Models can generate incorrect answers when they lack relevant context. Retrieval-Augmented Generation addresses this problem by retrieving relevant information from an external knowledge source and providing it to the LLM when answering a question.

This project explores a modular RAG architecture that separates document indexing, retrieval, API handling, and background processing.

## Features

### Implemented Components

- **Document indexing:** Load and split source documents into smaller chunks.
- **Vector embeddings:** Convert text chunks into vector representations using an embedding model.
- **Qdrant integration:** Store and retrieve document vectors using semantic similarity search.
- **Python API components:** Separate client, server, and worker modules.
- **Background processing:** Use RQ and a Redis-compatible queue backend to process queued jobs.
- **LLM integration:** Support LLM-based responses using retrieved context, where configured.

### Planned Features

- **Hybrid retrieval:** Combine BM25 keyword search with Qdrant vector similarity search.
- **PDF question answering:** Upload PDFs and ask questions about their content.
- **Video question answering:** Extract captions or transcribe audio and answer questions about video content.
- **Google Docs and Drive integration:** Retrieve content from authorized Google documents and answer questions about them.
- **Source attribution:** Return relevant document pages, source links, and video timestamps.
- **Multi-source retrieval:** Search across multiple indexed documents while keeping their source metadata separate.
- **Retrieval evaluation:** Compare vector search, BM25, and hybrid retrieval using a test dataset.

---

## Architecture

The system is organized around two workflows: document indexing and question answering.

### System Architecture

```test
flowchart TB
    subgraph INDEX["Document Indexing Pipeline"]
        A["Source Documents"] --> B["Document Loader"]
        B --> C["Text Chunking"]
        C --> D["Embedding Model"]
        D --> E[("Qdrant Vector Store")]
    end

    subgraph QUERY["Question Answering Pipeline"]
        U["User / Client"] --> API["Application API"]
        API --> Q["RQ Job Queue"]
        Q <--> R[("Redis-Compatible Backend")]
        Q --> W["RQ Worker"]
        W --> V["Qdrant Vector Retrieval"]
        E --> V
        V --> H["Retrieved Context"]
        H --> L["LLM Answer Generation"]
        L --> ANS["Generated Answer"]
        ANS --> U
    end

    subgraph FUTURE["Planned Retrieval Extensions"]
        M["BM25 Keyword Search"]
        P["PDF Ingestion"]
        VID["Video Captions / Transcripts"]
        G["Authorized Google Docs / Drive Access"]
    end

    P -.-> B
    VID -.-> B
    G -.-> B
    M -.-> H
```

*The main workflow illustrates the intended application architecture. The dashed connections represent planned extensions. The actual request and retrieval paths depend on the current implementation.*

### Indexing Workflow

1. Load a source document.
2. Extract and clean its text.
3. Split the text into manageable chunks.
4. Generate embeddings for the chunks.
5. Store vectors and associated metadata in Qdrant.

### Question-Answering Workflow

1. Receive a user's question through the client or API.
2. Enqueue the question for background processing when required.
3. Let the worker execute the retrieval pipeline.
4. Retrieve relevant chunks from Qdrant.
5. Provide the question and retrieved context to the LLM.
6. Return the generated answer to the user.

### Planned Hybrid Retrieval

The hybrid retrieval extension will combine two retrieval methods:

- **Vector search:** Finds semantically related content using embeddings.
- **BM25:** Finds content using keyword relevance.

Their results can be combined using a method such as Reciprocal Rank Fusion (RRF). This can improve retrieval when questions contain both conceptual descriptions and exact terms.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and retrieval logic |
| LangChain / LangChain integrations | Document and vector-store workflows, where used |
| OpenAI API | Embeddings and LLM responses, where configured |
| Qdrant | Vector storage and semantic search |
| FastAPI | API layer, where configured |
| RQ | Background job processing |
| Redis-compatible backend | Queue and job coordination |
| Docker | Local service management |

---

## Project Structure

```text
hybrid-rag-system/
├── 1.Indexing/
│   └── indexing.py
├── Client/
│   ├── __init__.py
│   └── rq_client.py
├── Queues/
│   ├── __init__.py
│   ├── main.py
│   ├── server.py
│   └── worker.py
├── .gitignore
├── docker-composer.yml
└── README.md
```

Additional modules such as `Retrieval/`, `Ingestion/`, and `requirements.txt` can be added as the project grows.

---

## Prerequisites

Before running the project, install or configure:

- Python compatible with your installed dependencies
- Docker Desktop
- A running Qdrant instance
- A Redis-compatible backend for RQ
- An OpenAI API key if your configured embedding or LLM code requires one

The service URLs, ports, queue names, and environment variables must match those used by the application.

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shubham4969/hybrid-rag-system.git
cd hybrid-rag-system
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages required by the project's Python imports.

A dependency file should be maintained so that setup is reproducible:

```powershell
pip install -r requirements.txt
```

This command requires a `requirements.txt` file to be added to the repository.

### 4. Configure environment variables

Create a local `.env` file containing the configuration required by your code.

For example, your application may require:

```dotenv
OPENAI_API_KEY=your_api_key
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
```

These are illustrative variable names. Use the exact names and values expected by your implementation and Docker configuration.

**Never commit real API keys, passwords, or private credentials to GitHub.**

### 5. Start the required services

Start Qdrant and the Redis-compatible queue backend. Ensure that both services are running and reachable at the URLs configured in your application.

Review `docker-composer.yml` before using it. The file must contain valid Docker Compose configuration for the services you intend to run.

If your Compose configuration is corrected and defines the required services, start them with:

```powershell
docker compose -f docker-composer.yml up -d
```

Check the status:

```powershell
docker compose -f docker-composer.yml ps
```

### 6. Run document indexing

Place a source document in the appropriate local location and run:

```powershell
python "1.Indexing/indexing.py"
```

The indexing process should finish successfully and store the generated vectors in the configured Qdrant collection.

### 7. Start the RQ worker

Start the worker using the queue name and connection settings expected by the application.

For a project configured to use the default queue and the standard RQ worker:

```powershell
rq worker
```

If your Windows environment requires the simple worker class, use the worker command appropriate to your existing setup.

Keep the worker terminal open while processing background jobs.

### 8. Start the API or application

Inspect `Queues/server.py` and `Queues/main.py` to identify the actual entry point.

For example, if `Queues/server.py` defines an ASGI application named `app`, it may be started with:

```powershell
uvicorn Queues.server:app --reload
```

The module and application variable must match your source code. Use the correct configured address when testing the API.

---

## How to Use the System

The current indexing pipeline can be tested by indexing a supported document and checking whether its vectors appear in Qdrant.

Once the query endpoint and retrieval pipeline are running:

1. Submit a question about the indexed document.
2. Allow the application to retrieve relevant chunks.
3. Pass the retrieved context to the configured LLM.
4. Inspect the answer for relevance and factual consistency.

The exact API endpoint and request format depend on the implementation in `Queues/server.py` and the client modules.

---

## Roadmap: Multi-Source RAG

### PDF Question Answering

Planned workflow:

1. Accept a PDF upload.
2. Extract text and page metadata.
3. Chunk the extracted text.
4. Generate embeddings and index the chunks.
5. Retrieve relevant passages to answer user questions.

### Video Question Answering

Planned workflow:

1. Accept a supported video URL or video upload.
2. Extract available captions or transcribe the audio.
3. Split the transcript into chunks and preserve timestamps.
4. Index the transcript for retrieval.
5. Answer questions using relevant transcript segments.

Answering questions about visual scenes will require an additional video-frame analysis pipeline.

### Google Docs and Drive Integration

Planned workflow:

1. Accept a Google Docs or Drive link.
2. Authenticate the user or use an authorized document access method.
3. Retrieve the permitted document content.
4. Extract text and metadata.
5. Index the content and answer questions using relevant retrieved chunks.

Private Google documents must not be accessed without appropriate authorization.

### Improved Retrieval and Evaluation

Future improvements include:

- BM25 keyword retrieval and hybrid ranking
- Reciprocal Rank Fusion
- Source references and citations
- Retrieval precision and recall measurements
- Automated tests for indexing and question answering
- Better error handling, retries, and logging

---

## Security and Limitations

- Keep secrets in local environment variables.
- Do not publish confidential documents or datasets without permission.
- Validate uploaded files and external URLs.
- Restrict Google document access to authorized content.
- Handle unavailable services and failed jobs gracefully.
- Evaluate generated answers rather than assuming every response is correct.
- Generated index artifacts should be reproducible wherever possible.

---

## Author

**Shubham Singh**

- GitHub: [@Shubham4969](https://github.com/Shubham4969)
- Project: [Hybrid RAG System](https://github.com/Shubham4969/hybrid-rag-system)

## License

Add a license file if you intend to distribute this project publicly. Choose a license that matches how you want others to use and modify your code.
