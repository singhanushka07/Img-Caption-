"""
Local development entry point.
Runs FastAPI on :8000 (background thread) and Gradio on :7860.
"""
import threading
import uvicorn
from app.main import app as fastapi_app
from ui.gradio_app import build_gradio_app


def _start_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="warning")


def main():
    t = threading.Thread(target=_start_fastapi, daemon=True)
    t.start()
    print("FastAPI  ->  http://localhost:8000")
    print("Gradio   ->  http://localhost:7860")

    from ui.gradio_app import CSS, JS, _THEME
    demo = build_gradio_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=CSS,
        js=JS,
        theme=_THEME,
    )


if __name__ == "__main__":
    main()
