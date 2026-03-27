import argparse
import json
import logging
from pathlib import Path
from typing import List

from app.discovery.sofascore_discovery import get_all_relevant_match_ids_sync
from app.services.browser_client import BrowserClient
from app.services.league_fetcher import LeagueFetcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Sofascore league context for ALL relevant matches (no IDs needed)."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/league_snapshots"),
        help="Directory to store JSON snapshots.",
    )
    return parser.parse_args()


def fetch_and_save(match_ids: List[int], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with BrowserClient() as client:
        fetcher = LeagueFetcher(client)

        for match_id in match_ids:
            logger.info("Processing match_id=%s", match_id)
            snapshot = fetcher.build_league_snapshot(match_id)

            out_path = output_dir / f"league_{match_id}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)

            logger.info("Saved %s", out_path)


def main() -> None:
    args = parse_args()

    logger.info("Starting FULL DISCOVERY (countries → tournaments → seasons → matches)...")
    match_ids = get_all_relevant_match_ids_sync()
    logger.info("Discovered %s matches", len(match_ids))

    fetch_and_save(match_ids, args.output_dir)


if __name__ == "__main__":
    main()
