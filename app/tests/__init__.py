from pathlib import Path
from dotenv import load_dotenv


test_env_path = Path(__file__).parent / ".test.env"
if test_env_path.exists():
    load_dotenv(test_env_path, override=True)


