from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/reset")
def reset():
    return {"observation": {}, "info": {}}

@app.post("/step")
def step():
    return {"observation": {}, "reward": 0.0, "done": False, "info": {}}

@app.get("/state")
def state():
    return {"state": {}}


def main():
    uvicorn.run(
        app,   # ✅ IMPORTANT: NOT "server.app:app"
        host="0.0.0.0",
        port=7860,
    )


if __name__ == "__main__":
    main()
