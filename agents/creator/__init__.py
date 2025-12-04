from typing import List
from models.audit_models import AuditData, AuditFinding
from models.report_models import ExecutiveSummary, FindingDetail, ActionPlan, Conclusion
from agents.creator.llm_factory import LLMFactory
from agents.creator.content_generator import ContentGenerator


class CreatorAgent:
    """Agent IA responsable de la génération enrichie des sections de rapport via LLM."""

    def __init__(self):
        self.llm = LLMFactory.create_llm()
        self.generator = ContentGenerator(self.llm)

    def generate_executive_summary(self, audit_data: AuditData) -> ExecutiveSummary:
        """Génère le résumé exécutif."""
        return self.generator.generate_executive_summary(audit_data)

    def enrich_finding(self, finding: AuditFinding, audit_data: AuditData) -> FindingDetail:
        """Enrichit un finding avec descriptions détaillées."""
        return self.generator.enrich_finding(finding, audit_data)

    def generate_action_plan(self, findings: List[FindingDetail], audit_data: AuditData) -> ActionPlan:
        """Génère le plan d'action priorisé."""
        return self.generator.generate_action_plan(findings, audit_data)

    def generate_conclusion(self, audit_data: AuditData, findings: List[FindingDetail]) -> Conclusion:
        """Génère la conclusion du rapport."""
        return self.generator.generate_conclusion(audit_data, findings)


__all__ = ["CreatorAgent"]