"""
Modèles de données pour les sections du rapport d'audit.
"""

from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from .audit_models import SeverityLevel, CategoryType, PriorityLevel


class CoverPage(BaseModel):
    """Page de garde du rapport."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(default="Rapport d'Audit de Sécurité", description="Titre du rapport")
    client_name: str = Field(..., description="Nom du client")
    audit_type: str = Field(..., description="Type d'audit")
    audit_date: date = Field(..., description="Date de l'audit")
    auditor: str = Field(..., description="Nom de l'auditeur")
    report_version: str = Field(default="1.0", description="Version du rapport")
    logo_path: Optional[str] = Field(None, description="Chemin vers le logo")


class ExecutiveSummary(BaseModel):
    """Résumé exécutif pour la direction."""

    model_config = ConfigDict(str_strip_whitespace=True)

    overview: str = Field(..., min_length=100, description="Vision synthétique de l'audit")
    global_risk_level: SeverityLevel = Field(..., description="Niveau de risque global")
    critical_count: int = Field(ge=0, description="Nombre de vulnérabilités critiques")
    high_count: int = Field(ge=0, description="Nombre de vulnérabilités hautes")
    medium_count: int = Field(ge=0, description="Nombre de vulnérabilités moyennes")
    low_count: int = Field(ge=0, description="Nombre de vulnérabilités basses")
    top_recommendations: List[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="3-5 recommandations prioritaires"
    )
    remediation_timeline: str = Field(..., description="Timeline suggérée de remédiation")


class ContextScope(BaseModel):
    """Contexte et périmètre de l'audit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    environment_description: str = Field(..., description="Description de l'environnement audité")
    technical_scope: str = Field(..., description="Périmètre technique (IP, domaines, etc.)")
    temporal_scope: str = Field(..., description="Périmètre temporel")
    constraints: Optional[str] = Field(None, description="Contraintes et limitations")
    contacts: Optional[str] = Field(None, description="Contacts et interlocuteurs")


class Methodology(BaseModel):
    """Méthodologie utilisée pour l'audit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    audit_type: str = Field(..., description="Type d'audit")
    standards: List[str] = Field(..., description="Standards et frameworks utilisés")
    tools: List[str] = Field(default_factory=list, description="Outils utilisés")
    phases: List[str] = Field(..., description="Phases de l'audit")
    approach: str = Field(..., description="Approche méthodologique")


class RiskMatrix(BaseModel):
    """Matrice des risques."""

    model_config = ConfigDict(str_strip_whitespace=True)

    matrix: Dict[str, Dict[str, int]] = Field(
        ...,
        description="Matrice likelihood × impact avec nombre de findings"
    )


class GlobalAnalysis(BaseModel):
    """Analyse globale du niveau de sécurité."""

    model_config = ConfigDict(str_strip_whitespace=True)

    security_score: float = Field(..., ge=0, le=100, description="Score global de sécurité")
    score_description: str = Field(..., description="Description du score")
    risk_matrix: RiskMatrix = Field(..., description="Matrice des risques")
    severity_distribution: Dict[str, int] = Field(..., description="Distribution par sévérité")
    category_distribution: Dict[str, float] = Field(..., description="Distribution par catégorie en %")
    sector_comparison: Optional[str] = Field(None, description="Comparaison sectorielle")


class FindingDetail(BaseModel):
    """Détail enrichi d'une vulnérabilité."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., description="Titre de la vulnérabilité")
    category: CategoryType = Field(..., description="Catégorie")
    enriched_description: str = Field(..., description="Description technique enrichie par l'IA")
    business_impact: str = Field(..., description="Impact métier analysé par l'IA")
    severity: SeverityLevel = Field(..., description="Sévérité")
    likelihood: SeverityLevel = Field(..., description="Probabilité d'exploitation")
    impact: SeverityLevel = Field(..., description="Impact")
    evidence: str = Field(..., description="Preuves")
    enriched_recommendation: str = Field(..., description="Recommandation détaillée par l'IA")
    priority: PriorityLevel = Field(..., description="Priorité d'action")


class ActionItem(BaseModel):
    """Item du plan d'action priorisé."""

    model_config = ConfigDict(str_strip_whitespace=True)

    measure: str = Field(..., description="Mesure de correction")
    priority: PriorityLevel = Field(..., description="Priorité")
    responsible: str = Field(..., description="Responsable suggéré")
    deadline: str = Field(..., description="Deadline suggérée")
    benefit: str = Field(..., description="Bénéfice métier")
    related_finding: Optional[str] = Field(None, description="Finding associé")


class ActionPlan(BaseModel):
    """Plan d'action priorisé."""

    model_config = ConfigDict(str_strip_whitespace=True)

    introduction: str = Field(..., description="Introduction au plan d'action")
    actions: List[ActionItem] = Field(..., min_length=1, description="Liste des actions")
    dependencies: Optional[str] = Field(None, description="Dépendances entre mesures")
    budget_estimate: Optional[str] = Field(None, description="Estimation budgétaire")


class Conclusion(BaseModel):
    """Conclusion du rapport."""

    model_config = ConfigDict(str_strip_whitespace=True)

    summary: str = Field(..., description="Récapitulatif du niveau de sécurité")
    positive_points: List[str] = Field(default_factory=list, description="Points positifs identifiés")
    improvement_areas: List[str] = Field(..., description="Axes d'amélioration majeurs")
    strategic_recommendations: List[str] = Field(..., description="Recommandations stratégiques")
    next_steps: str = Field(..., description="Perspectives et suivi")


class ReportSection(BaseModel):
    """Section générique du rapport."""

    model_config = ConfigDict(str_strip_whitespace=True)

    section_name: str = Field(..., description="Nom de la section")
    content: str = Field(..., description="Contenu de la section")
    validated: bool = Field(default=False, description="Section validée par le vérificateur")


class FullReport(BaseModel):
    """Rapport complet d'audit de sécurité."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Les 8 sections du rapport
    cover_page: CoverPage = Field(..., description="Page de garde")
    executive_summary: ExecutiveSummary = Field(..., description="Résumé exécutif")
    context_scope: ContextScope = Field(..., description="Contexte et périmètre")
    methodology: Methodology = Field(..., description="Méthodologie")
    global_analysis: GlobalAnalysis = Field(..., description="Analyse globale")
    findings: List[FindingDetail] = Field(..., description="Findings détaillés")
    action_plan: ActionPlan = Field(..., description="Plan d'action priorisé")
    conclusion: Conclusion = Field(..., description="Conclusion")

    # Métadonnées
    generation_timestamp: Optional[str] = Field(None, description="Timestamp de génération")
    generator_version: str = Field(default="1.0.0", description="Version du générateur")

    @property
    def total_pages_estimated(self) -> int:
        """Estimation du nombre de pages."""
        base_pages = 10  # Pages fixes
        findings_pages = len(self.findings) * 2  # 2 pages par finding en moyenne
        return base_pages + findings_pages
