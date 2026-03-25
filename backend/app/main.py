from fastapi import FastAPI
from app.routers import auth, stats

app = FastAPI()

app.include_router(auth.router)
app.include_router(stats.router)

import argparse
import json
import logging
from pathlib import Path
from typing import List

from app.services.browser_client import BrowserClient
from app.services.league_fetcher import LeagueFetcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Sofascore league context for one or more matches."
    )
    parser.add_argument(
        "match_ids",
        nargs="+",
        type=int,
        help="Sofascore match IDs (e.g. 15367402 15471607)",
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
    fetch_and_save(args.match_ids, args.output_dir)


if __name__ == "__main__":
    main()
