from dotenv import load_dotenv
from fastapi import FastAPI,Query
from Client.rq_client import queue
from Queues.worker import process_queue


load_dotenv()

app = FastAPI()

@app.get('/')
def root():
    return("server is running.")

@app.post('/chat')
def chat(
    query: str = Query(..., description="Enter your Query")
):
    job = queue.enqueue (process_queue, query)
    return{"status": "query", "job_id": job.id}


@app.get("/job_status")
def job_status(
    job_id: str = Query(..., description="Enter Job ID")
):
    job = queue.fetch_job(job_id)

    if job is None:
        return {
            "status": "Job not found"
        }

    return {
        "status": job.get_status(),
        "result": job.return_value()
    }
