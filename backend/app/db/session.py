from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

is_sqlite = "sqlite" in settings.DATABASE_URL
engine_kwargs = {"echo": False}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL async connection pool settings for high-concurrency production traffic
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

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
            if is_sqlite:
                res = connection.execute(text("PRAGMA table_info(patients)")).fetchall()
                existing = [c[1] for c in res]
                new_cols = [
                    ("phone", "VARCHAR(32)"),
                    ("abha_id", "VARCHAR(64)"),
                    ("state", "VARCHAR(64)"),
                    ("city", "VARCHAR(64)"),
                    ("emergency_contact", "VARCHAR(128)"),
                    ("username", "VARCHAR(64)"),
                    ("email", "VARCHAR(128)"),
                    ("hashed_password", "VARCHAR(255)"),
                ]
                for col, col_type in new_cols:
                    if col not in existing:
                        connection.execute(text(f"ALTER TABLE patients ADD COLUMN {col} {col_type}"))
                try:
                    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_patients_phone ON patients (phone)"))
                    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_username ON patients (username)"))
                    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_email ON patients (email)"))
                except Exception:
                    pass

        await conn.run_sync(sync_migrations)
