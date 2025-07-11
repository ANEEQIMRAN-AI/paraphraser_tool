from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from paraphraser import paraphraser_app

app = FastAPI()

# 🔐 Hardcoded Auth Credentials
VALID_EMAIL = "aneeq@example.com"
VALID_PASSWORD = "AneeQ@SecurePass123"

# 📦 Request Body Schema
class ParaphraseRequest(BaseModel):
    text: str
    style: Optional[str] = "Standard"

# 🔒 Dependency for Header-Based Authentication
async def verify_auth(
    x_api_secret_key: Optional[str] = Header(None),
    x_api_secret_value: Optional[str] = Header(None)
):
    if not x_api_secret_key or not x_api_secret_value:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authentication headers missing",
                "message": "Required: x-api-secret-key and x-api-secret-value"
            }
        )
    if x_api_secret_key != VALID_EMAIL or x_api_secret_value != VALID_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unauthorized",
                "message": "Invalid credentials"
            }
        )

# 🎯 Paraphrase Endpoint
@app.post("/paraphrase")
async def paraphrase_text(
    request_data: ParaphraseRequest,
    _: None = Depends(verify_auth)
):
    try:
        result = paraphraser_app.invoke({
            "input_paragraph": request_data.text,
            "style": request_data.style,
            "rephrased_paragraph": "",
            "llm_used": "",
            "error": None
        })

        return {
            "status": "success" if not result["error"] else "failure",
            "client": "ANEEQ",
            "original_text": request_data.text,
            "paraphrased_text": result["rephrased_paragraph"],
            "style": request_data.style,
            "llm_used": result["llm_used"],
            "error": result["error"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Server error occurred",
                "details": str(e)
            }
        )

# ✅ Enable Uvicorn when script is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
