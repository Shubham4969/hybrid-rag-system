from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
import gradio as gr
from rank_bm25 import BM25Okapi
import pickle

load_dotenv()
client = OpenAI()

chunk_path = Path(__file__).parent.parent / "1.Indexing" / "chunks.pkl"

with open(chunk_path, "rb") as f:
    chunks = pickle.load(f)

tokenized_corpus = [
    chunk.page_content.split()
    for chunk in chunks
]

bm25 = BM25Okapi(tokenized_corpus)


embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding= embedding_model,
    url= "http://localhost:6333",
    collection_name= "Rag done"
)

def process_queue(query: str):
    print("Search chunks:", query)

    query_tokens = query.split()

    bm25_results = bm25.get_top_n(
        query_tokens,
        chunks,
        n=5
    )

    for doc in bm25_results:
        print(doc.page_content[:200])

    vector_results = vector_db.similarity_search(
        query= query,
        k=5
        )
    combined_results = bm25_results + vector_results

    unique_docs = []
    seen = set()

    for doc in combined_results:

        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)


    context = "\n\n".join([
        f"""
        Source Type: {doc.metadata.get('source_type')}
        Source Name: {doc.metadata.get('source_name')}
        Page:{doc.metadata.get('page')}
        Timestamp:{doc.metadata.get('timestamp')}
        URL : {doc.metadata.get('url')}
        
        content:
        {doc.page_content}"""
        
        for doc in unique_docs
    ])
        
    SYSTEM_PROMPT = f"""
    
        You are an AI Customer Support Assistant.

        Answer the user's question only using the provided context.

        The context may come from:
        - PDF documents
        - Websites
        - YouTube transcripts

        If multiple sources provide the same information, combine them into one clear answer.

        If the sources contradict each other, clearly mention the contradiction.

        Always mention the source of the information:
        - PDF name and page number
        - Website URL
        - YouTube timestamp

        If the answer is not present in the context, reply:

        "I couldn't find this information in the available documents."

        Context:
        {context}

    """    

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query }
        ]
        
    )

    print(response.choices[0].message.content)
    answer =  response.choices[0].message.content
    return answer




demo = gr.ChatInterface(
        fn=lambda message, history: process_queue(message),
        title="My RAG Chatbot"
    )

demo.launch()

