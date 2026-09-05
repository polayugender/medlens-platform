from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def sync_migrations(connection):
            res = connection.execute(text("PRAGMA table_info(patients)")).fetchall()
            existing = [c[1] for c in res]
            new_cols = [
                ("phone", "VARCHAR(32)"),
                ("abha_id", "VARCHAR(64)"),
                ("state", "VARCHAR(64)"),
                ("city", "VARCHAR(64)"),
                ("emergency_contact", "VARCHAR(128)"),
            ]
            for col, col_type in new_cols:
                if col not in existing:
                    connection.execute(text(f"ALTER TABLE patients ADD COLUMN {col} {col_type}"))

        await conn.run_sync(sync_migrations)
