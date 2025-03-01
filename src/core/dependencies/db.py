from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from webtool.cache import RedisCache
from webtool.db import AsyncDB, SyncDB

Postgres = AsyncDB(settings.postgres_dsn.unicode_string())
Postgres_sync = SyncDB(settings.sync_postgres_dsn.unicode_string())
Redis = RedisCache(settings.redis_dsn.unicode_string())
Sqlite = SyncDB("sqlite:///:memory:")

postgres_session = Annotated[AsyncSession, Depends(Postgres)]
sqlite_session = Annotated[Session, Depends(Sqlite)]
