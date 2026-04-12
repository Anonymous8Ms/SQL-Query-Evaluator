from fastapi import FastAPI
import uvicorn

# Create FastAPI app
app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Server is running"}

# Reset endpoint
@app.post("/reset")
def reset():
    return {
        "observation": {},
        "info": {}
    }

# Step endpoint
@app.post("/step")
def step():
    return {
        "observation": {},
        "reward": 0.0,
        "done": False,
        "info": {}
    }

# State endpoint
@app.get("/state")
def state():
    return {"state": {}}


# IMPORTANT: main() must be callable by validator
def main():
    uvicorn.run(
        app,               # ✅ VERY IMPORTANT (not string)
        host="0.0.0.0",
        port=7860
    )


# REQUIRED for execution
if __name__ == "__main__":
    main()
