"""SQLModel schema for evaluation runs, test items, and scored results."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Text
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunStatus(str, Enum):
    """Lifecycle of an evaluation run."""

    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class Run(SQLModel, table=True):
    """One evaluation campaign: a test set + optional pipeline scores."""

    __tablename__ = "runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    pipeline_config_name: str = Field(
        default="baseline",
        index=True,
        description="Named RAG config used for this run (baseline/degraded/optimized).",
    )
    corpus_name: str = Field(default="default", index=True)
    num_questions: int = Field(default=0)
    status: str = Field(default=RunStatus.PENDING.value, index=True)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    test_items: List["TestItem"] = Relationship(back_populates="run")


class TestItem(SQLModel, table=True):
    """A single synthetic (or hand-written) question belonging to a Run."""

    __tablename__ = "test_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="runs.id", index=True)
    question: str = Field(sa_column=Column(Text, nullable=False))
    ground_truth_answer: str = Field(sa_column=Column(Text, nullable=False))
    reference_contexts: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
        description="Gold contexts used when the question was generated.",
    )
    question_type: str = Field(
        default="simple",
        index=True,
        description="simple | multi_hop | reasoning | abstain, etc.",
    )

    run: Optional[Run] = Relationship(back_populates="test_items")
    eval_results: List["EvalResult"] = Relationship(back_populates="test_item")


class EvalResult(SQLModel, table=True):
    """Pipeline output + Ragas scores for one TestItem."""

    __tablename__ = "eval_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    test_item_id: int = Field(foreign_key="test_items.id", index=True)
    generated_answer: Optional[str] = Field(default=None, sa_column=Column(Text))
    retrieved_contexts: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    faithfulness: Optional[float] = Field(default=None)
    answer_relevancy: Optional[float] = Field(default=None)
    context_precision: Optional[float] = Field(default=None)
    context_recall: Optional[float] = Field(default=None)
    context_entity_recall: Optional[float] = Field(default=None)
    answer_correctness: Optional[float] = Field(default=None)
    latency_ms: Optional[float] = Field(default=None)
    error: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    test_item: Optional[TestItem] = Relationship(back_populates="eval_results")


def row_to_dict(obj: SQLModel) -> Dict[str, Any]:
    """Serialize a SQLModel instance for logging / smoke checks."""
    return obj.model_dump()
