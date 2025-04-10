from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATASET_DIR = PROJECT_ROOT / "datasets"
LOG_DIR = PROJECT_ROOT / "logs"

# Model configuration
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_MODEL_TEMPERATURE = 0.7
DEFAULT_NUM_SAMPLES = 10
