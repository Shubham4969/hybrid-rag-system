from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import WebBaseLoader 
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import pickle

load_dotenv()

paths = Path(__file__).parent/"Employee-Handbook.pdf"

document = []

document.extend(
    PyPDFLoader("Employee-Handbook.pdf").load()
)

document.extend(
    WebBaseLoader("https://en.wikipedia.org/wiki/Extraterrestrial_life",
       
        ).load()
)

document.extend(
    YoutubeLoader.from_youtube_url(
        "https://www.youtube.com/watch?v=m7v7KLttM3k&t=6s",
        add_video_info = False
         ).load()

)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 300
)

chunks = text_splitter.split_documents(documents=document)

with open("chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)
    
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_documents(
    documents = chunks,
    embedding= embedding_model,
    url ="http://localhost:6333",
    collection_name = "Rag done"
)

print ("indexing done😎...")
