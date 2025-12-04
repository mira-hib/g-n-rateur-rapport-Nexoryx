"""
Agent créateur de sections de rapport.

Cet agent est responsable de générer le contenu de chaque section du rapport d'audit
en enrichissant les données brutes avec de l'intelligence artificielle.
"""

from typing import Dict, List, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from models.audit_models import AuditData, AuditFinding, SeverityLevel, PriorityLevel
from models.report_models import (
    ExecutiveSummary,
    FindingDetail,
    ActionPlan,
    ActionItem,
    Conclusion
)
from agents.prompt import AuditPrompts
from config.settings import settings


class CreatorAgent:
    """
    Agent créateur qui génère les sections du rapport d'audit.

    Responsabilités:
    - Générer le contenu de chaque section
    - Enrichir les descriptions techniques
    - Contextualiser pour le métier du client
    - Créer les analyses et recommandations
    - Générer le plan d'action priorisé
    """

    def __init__(self):
        """Initialise l'agent créateur avec le provider configuré."""
        self.provider = settings.ai_provider
        self.model_name = settings.get_model_name()
        self.llm = self._initialize_llm()

    def _initialize_llm(self) -> Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, HuggingFaceEndpoint]:
        """
        Initialise le modèle LLM selon le provider configuré.

        Returns:
            Instance du LLM configuré

        Raises:
            ValueError: Si le provider n'est pas supporté ou mal configuré
        """
        # Valider la configuration
        is_valid, error_msg = settings.validate_configuration()
        if not is_valid:
            raise ValueError(f"Configuration invalide: {error_msg}")

        # Initialiser selon le provider
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=settings.openai_api_key
            )

        elif self.provider == "claude":
            return ChatAnthropic(
                model=self.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                api_key=settings.anthropic_api_key
            )

        elif self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=settings.temperature,
                max_output_tokens=settings.max_tokens,
                google_api_key=settings.gemini_api_key
            )

        elif self.provider == "zephyr":
            return HuggingFaceEndpoint(
                repo_id=self.model_name,
                temperature=settings.temperature,
                max_new_tokens=settings.max_tokens,
                huggingfacehub_api_token=settings.huggingface_api_key
            )

        else:
            raise ValueError(f"Provider non supporté: {self.provider}")

    def generate_executive_summary(self, audit_data: AuditData) -> ExecutiveSummary:
        """
        Génère le résumé exécutif du rapport.

        Args:
            audit_data: Données de l'audit

        Returns:
            Résumé exécutif enrichi
        """
        top_findings_text = self._format_top_findings(audit_data.findings[:5])
        prompt = AuditPrompts.prompt_resume_executif(audit_data, top_findings_text)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        # Parse la réponse pour extraire les parties
        overview = self._extract_section(content, "vision synthétique", "recommandations")
        recommendations = self._extract_recommendations(content)
        timeline = self._extract_section(content, "timeline", None)

        # Déterminer le niveau de risque global
        if audit_data.critical_findings_count > 0:
            global_risk = SeverityLevel.CRITICAL
        elif audit_data.high_findings_count > 3:
            global_risk = SeverityLevel.HIGH
        elif audit_data.high_findings_count > 0:
            global_risk = SeverityLevel.MEDIUM
        else:
            global_risk = SeverityLevel.LOW

        return ExecutiveSummary(
            overview=overview or content[:500],
            global_risk_level=global_risk,
            critical_count=audit_data.critical_findings_count,
            high_count=audit_data.high_findings_count,
            medium_count=len([f for f in audit_data.findings if f.severity == SeverityLevel.MEDIUM]),
            low_count=len([f for f in audit_data.findings if f.severity == SeverityLevel.LOW]),
            top_recommendations=recommendations[:5] if recommendations else [
                "Corriger les vulnérabilités critiques en priorité",
                "Mettre en place un plan de remédiation",
                "Former les équipes aux bonnes pratiques"
            ],
            remediation_timeline=timeline or "Actions critiques: 1-2 semaines. Haute priorité: 1 mois. Autres: 1-3 mois."
        )

    def enrich_finding(self, finding: AuditFinding, audit_data: AuditData) -> FindingDetail:
        """
        Enrichit un finding avec des descriptions détaillées et une analyse d'impact métier.

        Args:
            finding: Finding à enrichir
            audit_data: Contexte de l'audit

        Returns:
            Finding enrichi avec description et recommandations IA
        """
        prompt = AuditPrompts.prompt_enrichissement_vulnerabilite(audit_data, finding)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        # Parse les différentes sections
        enriched_desc = self._extract_section(content, "description enrichie", "impact métier") or finding.description
        business_impact = self._extract_section(content, "impact métier", "recommandation enrichie") or "Impact métier significatif"
        enriched_rec = self._extract_section(content, "recommandation enrichie", None) or finding.recommendation

        # Déterminer la priorité
        priority = self._determine_priority(finding.severity)

        return FindingDetail(
            title=finding.title,
            category=finding.category,
            enriched_description=enriched_desc,
            business_impact=business_impact,
            severity=finding.severity,
            likelihood=finding.severity,  # Simplification: likelihood = severity
            impact=finding.severity,
            evidence=finding.evidence,
            enriched_recommendation=enriched_rec,
            priority=priority
        )

    def generate_action_plan(
        self,
        findings: List[FindingDetail],
        audit_data: AuditData
    ) -> ActionPlan:
        """
        Génère le plan d'action priorisé basé sur les findings.

        Args:
            findings: Liste des findings enrichis
            audit_data: Contexte de l'audit

        Returns:
            Plan d'action structuré et priorisé
        """
        findings_text =  self._format_findings_for_action_plan(findings)
        prompt = AuditPrompts.prompt_plan_action(audit_data, findings_text)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        # Parse l'introduction
        intro = self._extract_introduction(content)

        # Parse les actions
        actions = self._parse_actions(content, findings)

        # Extraire les dépendances
        dependencies = self._extract_section(content, "dépendances", None)

        return ActionPlan(
            introduction=intro,
            actions=actions,
            dependencies=dependencies,
            budget_estimate=None  # Optionnel pour MVP
        )

    def generate_conclusion(self, audit_data: AuditData, findings: List[FindingDetail]) -> Conclusion:
        """
        Génère la conclusion du rapport.

        Args:
            audit_data: Données de l'audit
            findings: Liste des findings enrichis

        Returns:
            Conclusion structurée
        """
        prompt = AuditPrompts.prompt_conclusion(audit_data, findings)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        # Parse les différentes sections
        summary = self._extract_section(content, "récapitulatif", "points positifs") or content[:200]
        positive = self._extract_list_items(content, "points positifs", "axes d'amélioration")
        improvement = self._extract_list_items(content, "axes d'amélioration", "recommandations stratégiques")
        strategic = self._extract_list_items(content, "recommandations stratégiques", "perspectives")
        next_steps = self._extract_section(content, "perspectives", None) or "Suivi recommandé dans 3 mois."

        return Conclusion(
            summary=summary,
            positive_points=positive[:5] if positive else ["Conscience des enjeux de sécurité"],
            improvement_areas=improvement[:5] if improvement else ["Renforcement de la sécurité"],
            strategic_recommendations=strategic[:5] if strategic else ["Établir une stratégie de sécurité"],
            next_steps=next_steps
        )

    # Méthodes utilitaires privées
    def _format_top_findings(self, findings: List[AuditFinding]) -> str:
        """Formate les top findings pour le prompt."""
        return "\n".join([f"- [{f.severity.value}] {f.title}" for f in findings])

    def _format_findings_for_action_plan(self, findings: List[FindingDetail]) -> str:
        """Formate les findings pour le prompt du plan d'action."""
        return "\n".join([
            f"{i+1}. [{f.priority.value}] {f.title} (Sévérité: {f.severity.value})"
            for i, f in enumerate(findings)
        ])

    def _extract_section(self, content: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extrait une section du contenu entre deux marqueurs."""
        content_lower = content.lower()
        start_idx = content_lower.find(start_marker.lower())

        if start_idx == -1:
            return ""

        # Chercher le début du contenu après le marqueur
        start_idx = content.find("\n", start_idx) + 1

        if end_marker:
            end_idx = content_lower.find(end_marker.lower(), start_idx)
            if end_idx != -1:
                return content[start_idx:end_idx].strip()

        return content[start_idx:].strip()

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extrait les recommandations d'un contenu."""
        recommendations = []
        lines = content.split("\n")

        in_recommendations = False
        for line in lines:
            if "recommandation" in line.lower():
                in_recommendations = True
                continue
            if in_recommendations and line.strip().startswith(("-", "•", "*", str(len(recommendations) + 1))):
                rec = line.strip().lstrip("-•*0123456789. ")
                if rec:
                    recommendations.append(rec)
            elif in_recommendations and "timeline" in line.lower():
                break

        return recommendations

    def _extract_list_items(self, content: str, start_marker: str, end_marker: str) -> List[str]:
        """Extrait une liste d'items entre deux marqueurs."""
        section = self._extract_section(content, start_marker, end_marker)
        items = []

        for line in section.split("\n"):
            line = line.strip()
            if line.startswith(("-", "•", "*")):
                item = line.lstrip("-•* ").strip()
                if item:
                    items.append(item)

        return items

    def _extract_introduction(self, content: str) -> str:
        """Extrait l'introduction du plan d'action."""
        lines = content.split("\n")
        intro_lines = []

        for line in lines:
            if any(keyword in line.lower() for keyword in ["mesure", "priorité", "action", "tableau"]):
                break
            if line.strip() and not line.strip().startswith("#"):
                intro_lines.append(line.strip())

        return " ".join(intro_lines) if intro_lines else "Plan d'action priorisé pour la remédiation des vulnérabilités."

    def _parse_actions(self, content: str, findings: List[FindingDetail]) -> List[ActionItem]:
        """Parse les actions du plan depuis le contenu généré."""
        actions = []
        lines = content.split("\n")

        for line in lines:
            # Chercher les lignes qui ressemblent à des actions
            if "|" in line and not line.strip().startswith("#"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    try:
                        actions.append(ActionItem(
                            measure=parts[0],
                            priority=self._parse_priority(parts[1]),
                            responsible=parts[2],
                            deadline=parts[3],
                            benefit=parts[4]
                        ))
                    except:
                        continue

        # Si pas d'actions parsées, créer des actions par défaut basées sur les findings
        if not actions:
            for finding in findings[:10]:
                actions.append(ActionItem(
                    measure=f"Corriger: {finding.title}",
                    priority=finding.priority,
                    responsible=self._suggest_responsible(finding.category),
                    deadline=self._suggest_deadline(finding.priority),
                    benefit=f"Réduction du risque {finding.severity.value}",
                    related_finding=finding.title
                ))

        return actions

    def _determine_priority(self, severity: SeverityLevel) -> PriorityLevel:
        """Détermine la priorité d'action selon la sévérité."""
        mapping = {
            SeverityLevel.CRITICAL: PriorityLevel.P0,
            SeverityLevel.HIGH: PriorityLevel.P1,
            SeverityLevel.MEDIUM: PriorityLevel.P2,
            SeverityLevel.LOW: PriorityLevel.P3
        }
        return mapping.get(severity, PriorityLevel.P2)

    def _parse_priority(self, priority_str: str) -> PriorityLevel:
        """Parse une chaîne de priorité."""
        priority_str = priority_str.upper().strip()
        if "P0" in priority_str or "IMMÉDIAT" in priority_str:
            return PriorityLevel.P0
        elif "P1" in priority_str or "COURT" in priority_str:
            return PriorityLevel.P1
        elif "P2" in priority_str or "MOYEN" in priority_str:
            return PriorityLevel.P2
        else:
            return PriorityLevel.P3

    def _suggest_responsible(self, category) -> str:
        """Suggère un responsable basé sur la catégorie."""
        mapping = {
            "Network": "NetOps / RSSI",
            "AppSec": "Dev Lead / AppSec",
            "IAM": "IT Admin / IAM Team",
            "Cloud": "Cloud Ops / DevOps",
            "Governance": "RSSI / CISO",
            "Forensic": "Incident Response Team"
        }
        return mapping.get(str(category), "RSSI")

    def _suggest_deadline(self, priority: PriorityLevel) -> str:
        """Suggère une deadline basée sur la priorité."""
        mapping = {
            PriorityLevel.P0: "1 semaine",
            PriorityLevel.P1: "1 mois",
            PriorityLevel.P2: "2-3 mois",
            PriorityLevel.P3: "3-6 mois"
        }
        return mapping.get(priority, "3 mois")
