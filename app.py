from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Server is running"}

@app.get("/reset")
def reset():
    return {"status": "reset done"}

@app.get("/step")
def step():
    return {"reward": 0.5, "done": False}

@app.get("/state")
def state():
    return {"data": "dummy state"}