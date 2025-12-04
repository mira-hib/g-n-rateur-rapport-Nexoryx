"""
Modèles d'état pour le workflow LangGraph.
"""

from enum import Enum
from typing import Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field, ConfigDict
from .audit_models import AuditData
from .report_models import ReportSection, FullReport


class ValidationStatus(str, Enum):
    """Statut de validation d'une section."""
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_CORRECTION = "needs_correction"
    FAILED = "failed"


class ValidationResult(BaseModel):
    """Résultat de la validation d'une section."""

    model_config = ConfigDict(str_strip_whitespace=True)

    section_name: str = Field(..., description="Nom de la section validée")
    status: ValidationStatus = Field(..., description="Statut de validation")
    issues: List[str] = Field(default_factory=list, description="Problèmes identifiés")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions d'amélioration")
    score: float = Field(ge=0, le=100, description="Score de qualité (0-100)")


class Correction(BaseModel):
    """Correction appliquée à une section."""

    model_config = ConfigDict(str_strip_whitespace=True)

    section_name: str = Field(..., description="Nom de la section corrigée")
    original_content: str = Field(..., description="Contenu original")
    corrected_content: str = Field(..., description="Contenu corrigé")
    reason: str = Field(..., description="Raison de la correction")
    iteration: int = Field(ge=1, description="Numéro d'itération")


class ReportState(TypedDict, total=False):
    """
    État du workflow de génération de rapport dans LangGraph.

    Attributes:
        audit_data: Données de l'audit récupérées de la base de données
        sections: Dictionnaire des sections générées (clé: nom de section)
        validation_results: Résultats de validation par le vérificateur
        corrections: Historique des corrections appliquées
        full_report: Rapport complet assemblé
        iteration: Numéro d'itération actuelle (max 3)
        current_section: Section en cours de traitement
        error: Message d'erreur éventuel
        metadata: Métadonnées supplémentaires
    """
    audit_data: AuditData
    sections: Dict[str, ReportSection]
    validation_results: List[ValidationResult]
    corrections: List[Correction]
    full_report: Optional[FullReport]
    iteration: int
    current_section: Optional[str]
    error: Optional[str]
    metadata: Dict[str, str]


class AgentResponse(BaseModel):
    """Réponse structurée d'un agent."""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., description="Contenu généré ou analysé")
    confidence: float = Field(ge=0, le=1, description="Niveau de confiance (0-1)")
    reasoning: Optional[str] = Field(None, description="Raisonnement de l'agent")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Métadonnées supplémentaires")
