import os
import shutil
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
import pika
from pika.adapters.blocking_connection import BlockingChannel
from typing import List

app = FastAPI()

CONNECTION: pika.BlockingConnection
CHANNEL: BlockingChannel


@app.on_event("startup")
async def startup_event():
    global CONNECTION
    print("Open queue connection")
    CONNECTION = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    global CHANNEL
    CHANNEL = CONNECTION.channel()
    CHANNEL.queue_declare(queue="train_photos", durable=True)
    CHANNEL.queue_declare(queue="generate_photos", durable=True)
    print("Queue declared")


@app.on_event("shutdown")
def shutdown_event():
    print("Closing channel")
    CHANNEL.close()
    print("Closing connection")
    CONNECTION.close()
    print("All closed")


@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile], session: str = Form()):
    counter = 0
    destination_path = os.path.join("sessions", session, "instance_images")
    shutil.rmtree(destination_path, ignore_errors=True)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    for file_upload in files:
        # Check if the file is a JPEG or PNG
        if file_upload.content_type in ["image/jpeg", "image/png"]:
            # Create the directory if it doesn't exist
            # Increment the counter
            counter += 1
            # Save the file to the directory with the session and counter in the filename
            with open(f"{destination_path}/ejxjo_{counter}.{file_upload.filename.split('.')[-1]}", "wb") as file:
                # Write the bytes to the file
                file.write(await file_upload.read())
    print("Before call queue")
    # Connect to the RabbitMQ server

    CHANNEL.basic_publish(
        exchange="", routing_key="train_photos", body=session)

    return {"filenames": [file.filename for file in files],  "session": session}


@ app.get("/sessions/")
def list_sessions():
    # Get the list of directories in the models folder
    sessions = [d for d in os.listdir(
        "models") if os.path.isdir(os.path.join("models", d))]
    # Return the list as a JSON response
    return {"sessions": sessions}


@ app.get("/test-queue/")
def test_queue():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost"))
    CHANNEL.basic_publish(
        exchange="", routing_key="train_photos", body="emanuele")


@app.get("/generate/")
def generate(session: str):
    CHANNEL.basic_publish(
        exchange="", routing_key="generate_photos", body=session)


@ app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="session" type="text">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

# launch with uvicorn server:app --reload
