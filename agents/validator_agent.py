"""
Agent vérificateur de qualité des sections de rapport.

Cet agent est responsable de valider la qualité, la cohérence et la complétude
des sections générées par l'agent créateur.
"""

from typing import List, Dict, Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from agents.prompt import AuditPrompts

from models.report_models import (
    ExecutiveSummary,
    FindingDetail,
    ActionPlan,
    Conclusion,
    ReportSection
)
from models.state_models import ValidationResult, ValidationStatus
from config.settings import settings


class ValidatorAgent:
    """
    Agent vérificateur qui valide la qualité des sections générées.

    Responsabilités:
    - Valider la cohérence du contenu
    - Vérifier la complétude des sections
    - Détecter les incohérences techniques
    - Évaluer la qualité rédactionnelle
    - Suggérer des corrections
    """

    def __init__(self):
        """Initialise l'agent vérificateur avec le provider configuré."""
        self.provider = settings.ai_provider
        self.model_name = settings.get_model_name()
        self.llm = self._initialize_llm()

    def _initialize_llm(self) -> Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, HuggingFaceEndpoint]:
        """
        Initialise le modèle LLM selon le provider configuré.
        Utilise une température plus basse (0.2) pour la validation.

        Returns:
            Instance du LLM configuré

        Raises:
            ValueError: Si le provider n'est pas supporté ou mal configuré
        """
        # Valider la configuration
        is_valid, error_msg = settings.validate_configuration()
        if not is_valid:
            raise ValueError(f"Configuration invalide: {error_msg}")

        # Température plus basse pour la validation (plus déterministe)
        validation_temperature = 0.2

        # Initialiser selon le provider
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=validation_temperature,
                max_tokens=settings.max_tokens,
                api_key=settings.openai_api_key
            )

        elif self.provider == "claude":
            return ChatAnthropic(
                model=self.model_name,
                temperature=validation_temperature,
                max_tokens=settings.max_tokens,
                api_key=settings.anthropic_api_key
            )

        elif self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=validation_temperature,
                max_output_tokens=settings.max_tokens,
                google_api_key=settings.gemini_api_key
            )

        elif self.provider == "zephyr":
            return HuggingFaceEndpoint(
                repo_id=self.model_name,
                temperature=validation_temperature,
                max_new_tokens=settings.max_tokens,
                huggingfacehub_api_token=settings.huggingface_api_key
            )

        else:
            raise ValueError(f"Provider non supporté: {self.provider}")

    def validate_executive_summary(
        self,
        summary: ExecutiveSummary,
        total_findings: int
    ) -> ValidationResult:
        """
        Valide le résumé exécutif.

        Args:
            summary: Résumé exécutif à valider
            total_findings: Nombre total de findings pour vérification

        Returns:
            Résultat de validation
        """
        prompt = AuditPrompts.prompt_validate_resume(summary, total_findings)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        # Parse la réponse
        score = self._extract_score(content)
        issues = self._extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self._extract_list(content, "SUGGESTIONS:", None)

        # Déterminer le statut
        if score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        return ValidationResult(
            section_name="Résumé Exécutif",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_finding(
        self,
        finding: FindingDetail,
        context: str = ""
    ) -> ValidationResult:
        """
        Valide un finding enrichi.

        Args:
            finding: Finding à valider
            context: Contexte additionnel (type d'audit, secteur, etc.)

        Returns:
            Résultat de validation
        """
        prompt = AuditPrompts.prompt_validate_finding(finding, context)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self._extract_score(content)
        issues = self._extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self._extract_list(content, "SUGGESTIONS:", None)

        if score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        return ValidationResult(
            section_name=f"Finding: {finding.title}",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_action_plan(
        self,
        action_plan: ActionPlan,
        findings_count: int
    ) -> ValidationResult:
        """
        Valide le plan d'action.

        Args:
            action_plan: Plan d'action à valider
            findings_count: Nombre de findings pour vérifier la cohérence

        Returns:
            Résultat de validation
        """
        prompt = AuditPrompts.prompt_validate_plan_action(
            action_plan, findings_count, self._format_actions_for_validation(action_plan.actions)
        )
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self._extract_score(content)
        issues = self._extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self._extract_list(content, "SUGGESTIONS:", None)

        if score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        return ValidationResult(
            section_name="Plan d'Action",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_conclusion(
        self,
        conclusion: Conclusion,
        context: str = ""
    ) -> ValidationResult:
        """
        Valide la conclusion du rapport.

        Args:
            conclusion: Conclusion à valider
            context: Contexte de l'audit

        Returns:
            Résultat de validation
        """
        prompt = AuditPrompts.prompt_validate_conclusion(conclusion, context)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self._extract_score(content)
        issues = self._extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self._extract_list(content, "SUGGESTIONS:", None)

        if score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        return ValidationResult(
            section_name="Conclusion",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_section(
        self,
        section: ReportSection,
        expected_length: int = 500
    ) -> ValidationResult:
        """
        Valide une section générique du rapport.

        Args:
            section: Section à valider
            expected_length: Longueur minimale attendue

        Returns:
            Résultat de validation
        """
        issues = []
        suggestions = []
        score = 100.0

        # Vérifications basiques
        if len(section.content) < expected_length:
            issues.append(f"Contenu trop court ({len(section.content)} < {expected_length} caractères)")
            score -= 20

        if not section.content.strip():
            issues.append("Contenu vide")
            score = 0.0
            status = ValidationStatus.FAILED
        elif score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        if not suggestions:
            suggestions.append("Section acceptable")

        return ValidationResult(
            section_name=section.section_name,
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def validate_full_report_coherence(
        self,
        sections: Dict[str, ReportSection]
    ) -> ValidationResult:
        """
        Valide la cohérence globale du rapport.

        Args:
            sections: Toutes les sections du rapport

        Returns:
            Résultat de validation de la cohérence globale
        """
        prompt = AuditPrompts.prompt_validate_full_report(sections, self._format_sections_for_coherence_check(sections))
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        score = self._extract_score(content)
        issues = self._extract_list(content, "PROBLÈMES:", "SUGGESTIONS:")
        suggestions = self._extract_list(content, "SUGGESTIONS:", None)

        if score >= settings.min_validation_score:
            status = ValidationStatus.APPROVED
        elif score >= 60:
            status = ValidationStatus.NEEDS_CORRECTION
        else:
            status = ValidationStatus.FAILED

        return ValidationResult(
            section_name="Cohérence Globale",
            status=status,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    # Méthodes utilitaires privées
    def _extract_score(self, content: str) -> float:
        """Extrait le score d'une réponse de validation."""
        import re
        match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", content, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 75.0  # Score par défaut

    def _extract_list(self, content: str, start_marker: str, end_marker: str | None) -> List[str]:
        """Extrait une liste d'items entre deux marqueurs."""
        items = []
        lines = content.split("\n")

        in_section = False
        for line in lines:
            if start_marker.upper() in line.upper():
                in_section = True
                continue
            if end_marker and end_marker.upper() in line.upper():
                break
            if in_section:
                line = line.strip()
                if line.startswith(("-", "•", "*")):
                    item = line.lstrip("-•* ").strip()
                    if item:
                        items.append(item)

        return items

    def _format_actions_for_validation(self, actions: List) -> str:
        """Formate les actions pour la validation."""
        return "\n".join([
            f"{i+1}. [{action.priority.value}] {action.measure} | "
            f"{action.responsible} | {action.deadline} | {action.benefit}"
            for i, action in enumerate(actions[:10])  # Limiter à 10 pour le prompt
        ])

    def _format_sections_for_coherence_check(self, sections: Dict[str, ReportSection]) -> str:
        """Formate les sections pour la vérification de cohérence."""
        formatted = []
        for name, section in list(sections.items())[:5]:  # Limiter pour taille du prompt
            preview = section.content[:200] + "..." if len(section.content) > 200 else section.content
            formatted.append(f"**{name}:**\n{preview}\n")
        return "\n".join(formatted)
