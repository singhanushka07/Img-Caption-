import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    blip_model_name: str = "Salesforce/blip-image-captioning-large"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    clip_score_threshold: float = 0.25
    llm_judge_threshold: int = 7

    yolo_model_name: str = "yolov8n.pt"
    yolo_confidence_threshold: float = 0.3

    complexity_edge_threshold: float = 0.15
    complexity_color_threshold: float = 50.0

    clip_image_weight: float = 0.4

    available_languages: list[str] = [
        "English", "Spanish", "French", "German",
        "Chinese", "Japanese", "Hindi",
    ]
    default_language: str = "English"

    confidence_clip_weight: float = 0.5
    confidence_judge_weight: float = 0.5

    faiss_index_path: str = "./data/faiss_index"
    mlflow_tracking_uri: str = "./mlruns"

    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    gradio_port: int = 7860

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def has_openai(self) -> bool:
        return bool(
            self.openai_api_key
            and self.openai_api_key not in ("", "your-api-key-here", "sk-...")
        )


settings = Settings()
