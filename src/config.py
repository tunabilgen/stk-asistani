"""Central configuration: paths, API endpoints and secrets loaded from .env."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional
    load_dotenv = None

ROOT = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(ROOT / ".env")

DATA = ROOT / "data"
RAW = DATA / "raw"
LIVE = RAW / "live"
HUMSET = RAW / "humset"
PROCESSED = DATA / "processed"
MODELS = ROOT / "models"
FIGURES = ROOT / "reports" / "figures"
WEB_DATA = ROOT / "web" / "data"
for _p in (LIVE, HUMSET, PROCESSED, MODELS, FIGURES, WEB_DATA):
    _p.mkdir(parents=True, exist_ok=True)

USER_AGENT = "stk-asistani/0.1 (student capstone, AI for SDGs)"

# --- LLM: DeepSeek via OpenRouter (OpenAI-compatible chat completions) ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4.1-flash")
# tried in order if the main model fails (e.g. no credit) — ":free" models cost nothing
LLM_FALLBACK_MODELS = [m for m in os.getenv(
    "LLM_FALLBACK_MODELS", "google/gemma-4-31b-it:free").split(",") if m.strip()]
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY") \
    or os.getenv("OPENCODE_API_KEY", "")

# Unified sector taxonomy used across the app.
# key -> (Turkish label, English label, HumSet label)
SECTORS = {
    "food":        ("Gıda Güvenliği", "Food Security", "Food Security"),
    "health":      ("Sağlık", "Health", "Health"),
    "wash":        ("Su ve Hijyen", "WASH", "WASH"),
    "shelter":     ("Barınma", "Shelter", "Shelter"),
    "education":   ("Eğitim", "Education", "Education"),
    "protection":  ("Koruma", "Protection", "Protection"),
    "nutrition":   ("Beslenme", "Nutrition", "Nutrition"),
    "livelihoods": ("Geçim Kaynakları", "Livelihoods", "Livelihoods"),
    "agriculture": ("Tarım", "Agriculture", "Agriculture"),
    "logistics":   ("Lojistik", "Logistics", "Logistics"),
}
HUMSET_TO_KEY = {v[2]: k for k, v in SECTORS.items()}
