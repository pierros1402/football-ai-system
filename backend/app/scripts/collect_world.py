import sys
import os
import logging

# ---------------------------------------------------------
# Force Python to load ONLY the correct backend
# ---------------------------------------------------------
sys.path.insert(0, "C:/projects/football-ai-system/backend")

from app.services.orchestrator import collect_all_world

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

if __name__ == "__main__":
    logging.info("🚀 Starting FULL WORLD COLLECTION job...")

    collect_all_world()

    logging.info("🏁 Job completed.")
