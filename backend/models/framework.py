"""Framework domain model (DATA_MODEL #2).

A Framework represents a framework, reporting standard, rating system,
or regulatory disclosure system. V0 examples include SSE, HKEX, GRI,
MSCI and CSA-COS, but the five sources are data, not code: they are
NOT hardcoded into the model.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import FrameworkType
from .ids import FRAMEWORK_PREFIX


class Framework(BaseModel):
    """One framework / reporting standard / rating system.

    ``framework_type`` carries the four canonical source categories:
    exchange_rule, reporting_standard, rating_methodology,
    rating_questionnaire.
    """

    model_config = ConfigDict(validate_assignment=True)

    framework_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    jurisdiction: str | None = None
    framework_type: FrameworkType
    # DATA_MODEL does not define controlled status values for Framework
    # in V0; keep it a free-form required string (example: "active").
    status: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("framework_id")
    @classmethod
    def _framework_id_shape(cls, value: str) -> str:
        if not value.startswith(FRAMEWORK_PREFIX):
            raise ValueError(
                f"framework_id must start with {FRAMEWORK_PREFIX!r}"
            )
        return value
