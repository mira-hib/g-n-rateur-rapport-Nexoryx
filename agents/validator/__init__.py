from typing import Dict
from models.report_models import ExecutiveSummary, FindingDetail, ActionPlan, Conclusion, ReportSection
from models.state_models import ValidationResult
from agents.creator.llm_factory import LLMFactory
from agents.validator.content_validator import ContentValidator


class ValidatorAgent:
    """Agent IA responsable de la validation qualité des sections de rapport via LLM."""

    def __init__(self):
        self.llm = LLMFactory.create_llm(temperature=0.2)
        self.validator = ContentValidator(self.llm)

    def validate_executive_summary(self, summary: ExecutiveSummary, total_findings: int) -> ValidationResult:
        """Valide le résumé exécutif."""
        return self.validator.validate_executive_summary(summary, total_findings)

    def validate_finding(self, finding: FindingDetail, context: str = "") -> ValidationResult:
        """Valide un finding enrichi."""
        return self.validator.validate_finding(finding, context)

    def validate_action_plan(self, action_plan: ActionPlan, findings_count: int) -> ValidationResult:
        """Valide le plan d'action."""
        return self.validator.validate_action_plan(action_plan, findings_count)

    def validate_conclusion(self, conclusion: Conclusion, context: str = "") -> ValidationResult:
        """Valide la conclusion."""
        return self.validator.validate_conclusion(conclusion, context)

    def validate_section(self, section: ReportSection, expected_length: int = 500) -> ValidationResult:
        """Valide une section générique."""
        return self.validator.validate_section(section, expected_length)

    def validate_full_report_coherence(self, sections: Dict[str, ReportSection]) -> ValidationResult:
        """Valide la cohérence globale du rapport."""
        return self.validator.validate_full_report_coherence(sections)


__all__ = ["ValidatorAgent"]