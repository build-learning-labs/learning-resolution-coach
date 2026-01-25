"""Standard agent response contract."""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class Signals(BaseModel):
    """Agent status signals."""
    
    adherence: float = Field(ge=0.0, le=1.0, description="Task completion rate")
    knowledge: float = Field(ge=0.0, le=1.0, description="Quiz/eval accuracy")
    retention: float = Field(ge=0.0, le=1.0, description="Concept retention score")
    status: Literal["active", "at_risk", "recovering"] = Field(
        default="active",
        description="User status based on engagement",
    )


class NextTask(BaseModel):
    """Recommended next task."""
    
    task: str = Field(description="Task description")
    timebox_min: int = Field(
        default=45,
        ge=10,
        le=120,
        description="Suggested time in minutes (20/45/90)",
    )
    type: Literal["reading", "coding", "review", "quiz"] = Field(
        default="reading",
        description="Task type",
    )
    priority: int = Field(default=1, ge=1, le=5, description="1 = highest priority")


class ResourceUsed(BaseModel):
    """Resource citation from RAG."""
    
    title: str = Field(description="Resource title")
    url: str = Field(description="Resource URL")
    relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score")


class Action(BaseModel):
    """Agent action recommendation."""
    
    plan_adjustment: Literal[
        "reduce_scope",
        "repeat_concepts", 
        "increase_challenge",
        "keep",
    ] = Field(default="keep", description="Plan modification")
    risk_mitigation: List[str] = Field(
        default_factory=list,
        description="Active risk mitigations",
    )


class AgentDecision(BaseModel):
    """Standard agent response contract for all endpoints.
    
    This schema ensures consistent, structured responses across
    all agent endpoints with observability signals.
    """
    
    reason: str = Field(description="Explanation of the decision")
    advice: Optional[str] = Field(default=None, description="Specific advice or feedback")
    signals: Signals = Field(description="Current status signals")
    action: Action = Field(
        default_factory=Action,
        description="Recommended actions",
    )
    next_tasks: List[NextTask] = Field(
        default_factory=list,
        description="Recommended next tasks",
    )
    resources_used: List[ResourceUsed] = Field(
        default_factory=list,
        description="RAG citations if applicable",
    )
    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Critic quality score",
    )
    quality_flags: List[str] = Field(
        default_factory=list,
        description="Quality issues if any",
    )
    
    # Observability
    trace_id: Optional[str] = Field(
        default=None,
        description="Opik trace ID",
    )


# Example usage:
# response = AgentDecision(
#     reason="User completed 4/5 tasks this week with good retention",
#     signals=Signals(adherence=0.8, knowledge=0.7, retention=0.6, status="active"),
#     action=Action(plan_adjustment="keep", risk_mitigation=["continue_pacing"]),
#     next_tasks=[
#         NextTask(task="Complete FastAPI tutorial chapter 3", timebox_min=45, type="reading"),
#     ],
#     resources_used=[
#         ResourceUsed(title="FastAPI Tutorial", url="https://fastapi.tiangolo.com/", relevance=0.9),
#     ],
#     quality_score=0.95,
#     quality_flags=[],
# )
