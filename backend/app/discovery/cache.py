import json
import aiosqlite
import asyncio
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
import time

CACHE_PATH = Path("cache/discovery_cache.db")
CACHE_PATH.parent.mkdir(exist_ok=True)

class DiscoveryCache:
    def __init__(self, db_path: Path = CACHE_PATH):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    hash TEXT,
                    timestamp REAL
                )
            """)
            await db.commit()

    async def set(self, key: str, value: Any):
        serialized = json.dumps(value, ensure_ascii=False)
        hash_value = hashlib.sha256(serialized.encode()).hexdigest()
        timestamp = time.time()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO cache (key, value, hash, timestamp)
                VALUES (?, ?, ?, ?)
            """, (key, serialized, hash_value, timestamp))
            await db.commit()

    async def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value, timestamp FROM cache WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return None

        value, timestamp = row

        if ttl is not None and (time.time() - timestamp) > ttl:
            return None

        return json.loads(value)

    async def get_hash(self, key: str) -> Optional[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT hash FROM cache WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()

        return row[0] if row else None

    async def clear(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache")
            await db.commit()
