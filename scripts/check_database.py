"""Check database tables after migration."""

from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://owl:owl_password@postgres:5432/owl_brain"
)

with engine.connect() as conn:
    # Check vector extension
    result = conn.execute(
        text("SELECT installed_version FROM pg_available_extensions WHERE name = 'vector'")
    )
    print(f"vector extension: {result.scalar()}")

    # List all tables
    result = conn.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
    )
    tables = [row[0] for row in result]
    print(f"Tables ({len(tables)}): {', '.join(tables)}")

    # Check alembic_version
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    print(f"Alembic version: {result.scalar()}")

print("Database check complete")
