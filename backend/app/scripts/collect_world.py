import logging
import time
from app.services.orchestrator import collect_all_world

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

if __name__ == "__main__":
    logging.info("🚀 Starting FULL WORLD COLLECTION job...")

    # Full world discovery + collection
    collect_all_world(years_back=10)

    logging.info("🏁 Job completed.")
