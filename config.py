from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: str = "./upload_files"
    output_dir: str = "./generated_images"
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
