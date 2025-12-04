"""
Modèles de données pour le système de génération de rapports d'audit.
"""

from .audit_models import (
    AuditData,
    AuditFinding,
    AuditMetadata,
    SeverityLevel,
    CategoryType,
    PriorityLevel
)

from .report_models import (
    CoverPage,
    ExecutiveSummary,
    ContextScope,
    Methodology,
    GlobalAnalysis,
    FindingDetail,
    ActionPlan,
    ActionItem,
    Conclusion,
    ReportSection,
    FullReport
)

from .state_models import (
    ReportState,
    ValidationResult,
    Correction,
    ValidationStatus
)

__all__ = [
    # Audit models
    "AuditData",
    "AuditFinding",
    "AuditMetadata",
    "SeverityLevel",
    "CategoryType",
    "PriorityLevel",

    # Report models
    "CoverPage",
    "ExecutiveSummary",
    "ContextScope",
    "Methodology",
    "GlobalAnalysis",
    "FindingDetail",
    "ActionPlan",
    "ActionItem",
    "Conclusion",
    "ReportSection",
    "FullReport",

    # State models
    "ReportState",
    "ValidationResult",
    "Correction",
    "ValidationStatus"
]
