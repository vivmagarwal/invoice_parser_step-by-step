"""
Static File and Homepage Routes

Handles static file serving and the main application interface.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["static"])


@router.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serves the main application interface."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <h1>Invoice Parser</h1>
            <p>Frontend not found. Please check static/index.html</p>
            <p>API documentation available at <a href="/docs">/docs</a></p>
            """,
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error serving homepage: {str(e)}"
        )


