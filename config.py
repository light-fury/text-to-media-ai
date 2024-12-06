#config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_URI = os.getenv("DATABASE_URI", "sqlite:///ai_generation.db")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RUNWAYML_API_SECRET = os.getenv("RUNWAYML_API_SECRET")
