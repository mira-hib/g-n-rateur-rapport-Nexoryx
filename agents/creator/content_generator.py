from typing import List
from models.audit_models import AuditData, AuditFinding, SeverityLevel
from models.report_models import ExecutiveSummary, FindingDetail, ActionPlan, Conclusion
from agents.prompts import AuditPrompts
from agents.creator.parser_utils import ParserUtils


class ContentGenerator:
    """Générateur de contenu enrichi via LLM pour les sections de rapport."""

    def __init__(self, llm):
        self.llm = llm
        self.parser = ParserUtils()

    def generate_executive_summary(self, audit_data: AuditData) -> ExecutiveSummary:
        """Génère le résumé exécutif enrichi par LLM."""
        top_findings_text = self.parser.format_top_findings(audit_data.findings[:5])
        prompt = AuditPrompts.prompt_resume_executif(audit_data, top_findings_text)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        overview = self.parser.extract_section(content, "vision synthétique", "recommandations")
        recommendations = self.parser.extract_recommendations(content)
        timeline = self.parser.extract_section(content, "timeline", None)

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
        """Enrichit un finding avec descriptions détaillées via LLM."""
        prompt = AuditPrompts.prompt_enrichissement_vulnerabilite(audit_data, finding)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        enriched_desc = self.parser.extract_section(content, "description enrichie", "impact métier") or finding.description
        business_impact = self.parser.extract_section(content, "impact métier", "recommandation enrichie") or "Impact métier significatif"
        enriched_rec = self.parser.extract_section(content, "recommandation enrichie", None) or finding.recommendation
        priority = self.parser.determine_priority(finding.severity)

        return FindingDetail(
            title=finding.title,
            category=finding.category,
            enriched_description=enriched_desc,
            business_impact=business_impact,
            severity=finding.severity,
            likelihood=finding.severity,
            impact=finding.severity,
            evidence=finding.evidence,
            enriched_recommendation=enriched_rec,
            priority=priority
        )

    def generate_action_plan(self, findings: List[FindingDetail], audit_data: AuditData) -> ActionPlan:
        """Génère le plan d'action priorisé via LLM."""
        findings_text = self.parser.format_findings_for_action_plan(findings)
        prompt = AuditPrompts.prompt_plan_action(audit_data, findings_text)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        intro = self.parser.extract_introduction(content)
        actions = self.parser.parse_actions(content, findings)
        dependencies = self.parser.extract_section(content, "dépendances", None)

        return ActionPlan(
            introduction=intro,
            actions=actions,
            dependencies=dependencies,
            budget_estimate=None
        )

    def generate_conclusion(self, audit_data: AuditData, findings: List[FindingDetail]) -> Conclusion:
        """Génère la conclusion du rapport via LLM."""
        prompt = AuditPrompts.prompt_conclusion(audit_data, findings)
        response = self.llm.invoke(prompt.format_messages())
        content = response.content

        summary = self.parser.extract_section(content, "récapitulatif", "points positifs") or content[:200]
        positive = self.parser.extract_list_items(content, "points positifs", "axes d'amélioration")
        improvement = self.parser.extract_list_items(content, "axes d'amélioration", "recommandations stratégiques")
        strategic = self.parser.extract_list_items(content, "recommandations stratégiques", "perspectives")
        next_steps = self.parser.extract_section(content, "perspectives", None) or "Suivi recommandé dans 3 mois."

        return Conclusion(
            summary=summary,
            positive_points=positive[:5] if positive else ["Conscience des enjeux de sécurité"],
            improvement_areas=improvement[:5] if improvement else ["Renforcement de la sécurité"],
            strategic_recommendations=strategic[:5] if strategic else ["Établir une stratégie de sécurité"],
            next_steps=next_steps
        )
