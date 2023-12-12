import os
import logging
from api import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-16s %(levelname)-8s %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("OPENAI_API_KEY not defined as an environment variable")

if __name__ == "__main__":
    pass
