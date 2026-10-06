from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, desc, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent / "repairlens.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    device_category: Mapped[str] = mapped_column(String(80), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    problem_description: Mapped[str] = mapped_column(Text, nullable=False)
    possible_problem: Mapped[str] = mapped_column(String(240), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    repair_or_replace: Mapped[str] = mapped_column(String(30), default="Review")
    likely_component: Mapped[str | None] = mapped_column(String(240), nullable=True)
    price_confidence: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_basis: Mapped[str | None] = mapped_column(String(40), nullable=True)


Base.metadata.create_all(engine)

with engine.begin() as connection:
    existing_columns = {column["name"] for column in inspect(engine).get_columns("diagnoses")}
    migrations = {
        "likely_component": "VARCHAR(240)",
        "price_confidence": "VARCHAR(30)",
        "reason": "TEXT",
        "analysis_basis": "VARCHAR(40)",
    }
    for column_name, column_type in migrations.items():
        if column_name not in existing_columns:
            connection.execute(text(f"ALTER TABLE diagnoses ADD COLUMN {column_name} {column_type}"))
            existing_columns.add(column_name)


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_diagnosis(session: Session, **values) -> Diagnosis:
    diagnosis = Diagnosis(**values)
    session.add(diagnosis)
    session.flush()
    return diagnosis


def get_diagnoses(limit: int | None = None) -> list[Diagnosis]:
    with get_session() as session:
        statement = select(Diagnosis).order_by(desc(Diagnosis.date))
        if limit:
            statement = statement.limit(limit)
        return list(session.scalars(statement).all())
