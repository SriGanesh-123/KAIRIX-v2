from __future__ import annotations

from typing import Any, Type, TypeVar
from pydantic import BaseModel, ValidationError

from ..models.knowledge_models import (
    ArtifactKnowledgeProfile,
    ArtifactReview,
    CanonicalMetadata,
    EntityItem,
    KnowledgePackage,
    ReconciliationReport,
    RelationshipItem,
    SourceMetadata,
    SourceSummary,
    TransformationRule,
)

T = TypeVar("T", bound=BaseModel)


class KnowledgeValidationError(Exception):
    """Raised when knowledge data fails Pydantic schema validation."""


class KnowledgeValidator:
    """
    Validates dictionary payloads against the strict Pydantic Knowledge models.
    """

    @staticmethod
    def validate_model(data: dict[str, Any], model_cls: Type[T]) -> T:
        try:
            return model_cls.model_validate(data)
        except ValidationError as e:
            raise KnowledgeValidationError(
                f"Validation failed for {model_cls.__name__}: {e}"
            ) from e

    @classmethod
    def validate_source_summary(cls, data: dict[str, Any]) -> SourceSummary:
        return cls.validate_model(data, SourceSummary)

    @classmethod
    def validate_knowledge_profile(cls, data: dict[str, Any]) -> ArtifactKnowledgeProfile:
        return cls.validate_model(data, ArtifactKnowledgeProfile)

    @classmethod
    def validate_reconciliation(cls, data: dict[str, Any]) -> ReconciliationReport:
        return cls.validate_model(data, ReconciliationReport)

    @classmethod
    def validate_canonical_metadata(cls, data: dict[str, Any]) -> CanonicalMetadata:
        return cls.validate_model(data, CanonicalMetadata)

    @classmethod
    def validate_knowledge_package(cls, data: dict[str, Any]) -> KnowledgePackage:
        return cls.validate_model(data, KnowledgePackage)

    @classmethod
    def validate_artifact_review(cls, data: dict[str, Any]) -> ArtifactReview:
        return cls.validate_model(data, ArtifactReview)
