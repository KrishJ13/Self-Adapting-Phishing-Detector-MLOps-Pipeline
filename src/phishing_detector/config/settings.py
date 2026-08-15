from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache # Import from functools

class Settings(BaseSettings):
    """
    BaseSettings reads the enviornment variables and Pydantic (behind the scene) validates it against their declared types
    """
    # It is good practice to use a specific prefix to avoid any conflicting environment variables
    model_config = SettingsConfigDict(env_file=".env", env_prefix="PHISHING_", extra="forbid") # using .env is a development practice, it should be gitignored

    # Both environment and log_level must be provided
    environment: Literal["development", "production", "testing"] # Allow only these "states" of the project
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # The maximum False Postive Rate the model should have
    max_FPR: float = Field(default=0.01, gt=0.0, le=1.0)
    # The maximum % of all traffic the human reviewer must be exposed to
    max_review_rate : float = Field(default=0.05, gt=0.0, le=1.0)
    # The maximum latency - Must be 0 or more
    max_p95_latency_ms: int = Field(gt=0)

"""
Decorator 'lru_cache' tells Python to run the following function once, and save the result in cache, so that the next
time the call is repeated (with the same parameters), the cached result is provided, instead of re-running the function
"""
# Good practice to use lru_cache for the settings here, because they may be called repeatedly in different modules, but setting won't change during runtime
@lru_cache
def import_settings() -> Settings:
    return Settings()

