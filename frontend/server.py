import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import Body, FastAPI
import uvicorn


load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)

@app.post("/api/chat")
def chat(payload=Body(...)):
    history = payload['history']
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=history,        
        temperature=0.1
    )

    return {"reply": completion.choices[0].message.content}


if __name__ == "__main__":
    uvicorn.run("server:app", reload=True)