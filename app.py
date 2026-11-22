"""
HuggingFace Spaces / standalone entry point.
Launches the Gradio UI on port 7860.
"""
from ui.gradio_app import build_gradio_app, CSS, JS, _THEME

demo = build_gradio_app()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=CSS,
        js=JS,
        theme=_THEME,
    )
