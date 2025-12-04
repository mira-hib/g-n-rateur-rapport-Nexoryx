"""
Modèles de données pour les audits de sécurité.
"""

from datetime import date
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class SeverityLevel(str, Enum):
    """Niveaux de sévérité des vulnérabilités."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CategoryType(str, Enum):
    """Catégories de vulnérabilités."""
    NETWORK = "Network"
    APPSEC = "AppSec"
    IAM = "IAM"
    CLOUD = "Cloud"
    GOVERNANCE = "Governance"
    FORENSIC = "Forensic"


class PriorityLevel(str, Enum):
    """Niveaux de priorité d'action."""
    P0 = "P0"  # Immédiat (< 1 semaine)
    P1 = "P1"  # Court terme (< 1 mois)
    P2 = "P2"  # Moyen terme (1-3 mois)
    P3 = "P3"  # Long terme (> 3 mois)


class AuditFinding(BaseModel):
    """Représente une vulnérabilité identifiée lors d'un audit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = Field(None, description="ID du finding dans la base de données")
    title: str = Field(..., min_length=1, description="Titre de la vulnérabilité")
    description: str = Field(..., min_length=1, description="Description technique")
    severity: SeverityLevel = Field(..., description="Niveau de sévérité")
    evidence: str = Field(..., description="Preuves et captures")
    recommendation: str = Field(..., description="Recommandations de correction")
    category: CategoryType = Field(..., description="Catégorie de la vulnérabilité")

    # Champs enrichis par l'IA
    enriched_description: Optional[str] = Field(None, description="Description enrichie par l'IA")
    business_impact: Optional[str] = Field(None, description="Impact métier analysé par l'IA")
    enriched_recommendation: Optional[str] = Field(None, description="Recommandation détaillée par l'IA")
    priority: Optional[PriorityLevel] = Field(None, description="Priorité d'action")

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.title} ({self.category.value})"


class AuditMetadata(BaseModel):
    """Métadonnées contextuelles d'un audit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    key: str = Field(..., description="Clé de la métadonnée")
    value: str = Field(..., description="Valeur de la métadonnée")


class AuditData(BaseModel):
    """Données complètes d'un audit de sécurité."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Informations générales
    id: int = Field(..., description="ID de l'audit")
    client_name: str = Field(..., min_length=1, description="Nom du client")
    audit_type: str = Field(..., min_length=1, description="Type d'audit (Pentest, ISO27001, etc.)")
    audit_date: date = Field(..., description="Date de l'audit")
    auditor: str = Field(..., min_length=1, description="Nom de l'auditeur")
    scope: str = Field(..., description="Périmètre de l'audit")

    # Findings et métadonnées
    findings: List[AuditFinding] = Field(default_factory=list, description="Liste des vulnérabilités")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Métadonnées contextuelles")

    @property
    def findings_by_severity(self) -> Dict[SeverityLevel, List[AuditFinding]]:
        """Groupe les findings par niveau de sévérité."""
        result: Dict[SeverityLevel, List[AuditFinding]] = {
            SeverityLevel.CRITICAL: [],
            SeverityLevel.HIGH: [],
            SeverityLevel.MEDIUM: [],
            SeverityLevel.LOW: []
        }
        for finding in self.findings:
            result[finding.severity].append(finding)
        return result

    @property
    def findings_by_category(self) -> Dict[CategoryType, List[AuditFinding]]:
        """Groupe les findings par catégorie."""
        result: Dict[CategoryType, List[AuditFinding]] = {}
        for finding in self.findings:
            if finding.category not in result:
                result[finding.category] = []
            result[finding.category].append(finding)
        return result

    @property
    def total_findings(self) -> int:
        """Nombre total de findings."""
        return len(self.findings)

    @property
    def critical_findings_count(self) -> int:
        """Nombre de findings critiques."""
        return len([f for f in self.findings if f.severity == SeverityLevel.CRITICAL])

    @property
    def high_findings_count(self) -> int:
        """Nombre de findings haute sévérité."""
        return len([f for f in self.findings if f.severity == SeverityLevel.HIGH])

    def get_metadata(self, key: str, default: str = "") -> str:
        """Récupère une métadonnée par sa clé."""
        return self.metadata.get(key, default)
