from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with Gunicorn!"}

if __name__ == "__main__":
    # Run Gunicorn programmatically and bind it (oh daddy) to port 5000
    subprocess.run([
        "gunicorn",
        "-w", "1",  # Number of workers
        "-k", "uvicorn.workers.UvicornWorker",  # Use Uvicorn worker
        "-b", "0.0.0.0:5000",  # Bind to host and port
        "main:app"
    ])
