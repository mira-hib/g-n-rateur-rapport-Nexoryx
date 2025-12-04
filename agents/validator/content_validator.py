from typing import Dict
from models.report_models import ExecutiveSummary, FindingDetail, ActionPlan, Conclusion, ReportSection
from models.state_models import ValidationResult, ValidationStatus
from agents.prompts import AuditPrompts
from agents.validator.parser_utils import ValidationParser
from config.settings import settings


class ContentValidator:
    """Validateur de qualité pour les sections de rapport via LLM."""

    def __init__(self, llm):
        self.llm = llm
        self.parser = ValidationParser()

    def validate_executive_summary(self, summary: ExecutiveSummary, total_findings: int) -> ValidationResult:
        """Valide le résumé exécutif."""
        prompt = AuditPrompts.prompt_validate_resume(summary, total_findings)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self.parser.extract_score(content)
        issues = self.parser.extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self.parser.extract_list(content, "SUGGESTIONS:", None)
        status = self._determine_status(score)

        return ValidationResult(
            section_name="Résumé Exécutif",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_finding(self, finding: FindingDetail, context: str = "") -> ValidationResult:
        """Valide un finding enrichi."""
        prompt = AuditPrompts.prompt_validate_finding(finding, context)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self.parser.extract_score(content)
        issues = self.parser.extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self.parser.extract_list(content, "SUGGESTIONS:", None)
        status = self._determine_status(score)

        return ValidationResult(
            section_name=f"Finding: {finding.title}",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_action_plan(self, action_plan: ActionPlan, findings_count: int) -> ValidationResult:
        """Valide le plan d'action."""
        format_actions = self.parser.format_actions_for_validation(action_plan.actions)
        prompt = AuditPrompts.prompt_validate_plan_action(action_plan, findings_count, format_actions)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self.parser.extract_score(content)
        issues = self.parser.extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self.parser.extract_list(content, "SUGGESTIONS:", None)
        status = self._determine_status(score)

        return ValidationResult(
            section_name="Plan d'Action",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_conclusion(self, conclusion: Conclusion, context: str = "") -> ValidationResult:
        """Valide la conclusion du rapport."""
        prompt = AuditPrompts.prompt_validate_conclusion(conclusion, context)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self.parser.extract_score(content)
        issues = self.parser.extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self.parser.extract_list(content, "SUGGESTIONS:", None)
        status = self._determine_status(score)

        return ValidationResult(
            section_name="Conclusion",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_section(self, section: ReportSection, expected_length: int = 500) -> ValidationResult:
        """Valide une section générique basée sur des règles simples."""
        issues = []
        suggestions = []
        score = 100.0

        if len(section.content) < expected_length:
            issues.append(f"Contenu trop court ({len(section.content)} < {expected_length} caractères)")
            score -= 20

        if not section.content.strip():
            issues.append("Contenu vide")
            score = 0.0
            status = ValidationStatus.FAILED
        else:
            status = self._determine_status(score)

        if not suggestions:
            suggestions.append("Section acceptable")

        return ValidationResult(
            section_name=section.section_name,
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_full_report_coherence(self, sections: Dict[str, ReportSection]) -> ValidationResult:
        """Valide la cohérence globale du rapport."""
        format_sections = self.parser.format_sections_for_coherence_check(sections)
        prompt = AuditPrompts.prompt_validate_full_report(sections, format_sections)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self.parser.extract_score(content)
        issues = self.parser.extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self.parser.extract_list(content, "SUGGESTIONS:", None)
        status = self._determine_status(score)

        return ValidationResult(
            section_name="Cohérence Globale",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def _determine_status(self, score: float) -> ValidationStatus:
        """Détermine le statut de validation selon le score."""
        if score >= settings.min_validation_score:
            return ValidationStatus.APPROVED
        elif score >= 60:
            return ValidationStatus.NEEDS_CORRECTION
        else:
            return ValidationStatus.FAILED
