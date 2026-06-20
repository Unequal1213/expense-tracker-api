from datetime import UTC, datetime


def test_models_define_expected_tables(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@localhost:5432/test_db",
    )

    from app.database.database import Base
    from app.models import Category, Transaction

    assert Category.__tablename__ == "categories"
    assert Transaction.__tablename__ == "transactions"
    assert {"categories", "transactions"} <= set(Base.metadata.tables)


def test_model_timestamps_are_timezone_aware(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:password@localhost:5432/test_db",
    )

    from app.models.category import utc_now

    timestamp = utc_now()

    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo is UTC
