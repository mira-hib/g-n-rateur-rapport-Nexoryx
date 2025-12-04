from datetime import datetime
from typing import List
from models.audit_models import SeverityLevel
from models.report_models import (
    CoverPage, ExecutiveSummary, ContextScope, Methodology,
    GlobalAnalysis, FindingDetail, ActionPlan, Conclusion,
    ReportSection, RiskMatrix, FullReport
)
from models.state_models import ReportState, ValidationStatus
from config.settings import settings


class WorkflowNodes:
    """Nœuds de traitement du workflow LangGraph pour la génération de rapport."""

    def __init__(self, creator_agent, validator_agent):
        self.creator = creator_agent
        self.validator = validator_agent

    def initialize_state(self, state: ReportState) -> ReportState:
        state["iteration"] = 0
        state["metadata"]["start_time"] = datetime.now().isoformat()
        return state

    def generate_cover_page(self, state: ReportState) -> ReportState:
        audit_data = state["audit_data"]
        cover = CoverPage(
            client_name=audit_data.client_name,
            audit_type=audit_data.audit_type,
            audit_date=audit_data.audit_date,
            auditor=audit_data.auditor
        )
        state["sections"]["cover_page"] = ReportSection(
            section_name="Page de Garde",
            content=f"Rapport d'Audit - {cover.client_name}",
            validated=True
        )
        state["metadata"]["cover_page"] = cover.model_dump()
        return state

    def generate_executive_summary(self, state: ReportState) -> ReportState:
        state["current_section"] = "executive_summary"
        audit_data = state["audit_data"]
        summary = self.creator.generate_executive_summary(audit_data)
        state["sections"]["executive_summary"] = ReportSection(
            section_name="Résumé Exécutif",
            content=summary.overview
        )
        state["metadata"]["executive_summary"] = summary.model_dump()
        return state

    def generate_context_scope(self, state: ReportState) -> ReportState:
        audit_data = state["audit_data"]
        context = ContextScope(
            environment_description=f"Environnement {audit_data.audit_type} pour {audit_data.client_name}",
            technical_scope=audit_data.scope,
            temporal_scope=f"Audit réalisé le {audit_data.audit_date.isoformat()}",
            constraints="Contraintes selon le périmètre défini",
            contacts=f"Auditeur: {audit_data.auditor}"
        )
        state["sections"]["context_scope"] = ReportSection(
            section_name="Contexte & Périmètre",
            content=context.technical_scope,
            validated=True
        )
        state["metadata"]["context_scope"] = context.model_dump()
        return state

    def generate_methodology(self, state: ReportState) -> ReportState:
        audit_data = state["audit_data"]
        standards_map = {
            "Pentest": ["OWASP", "PTES", "OSSTMM"],
            "ISO": ["ISO 27001", "ISO 27002"],
            "SOC2": ["AICPA TSC"],
            "Cloud": ["CIS Benchmarks", "AWS Well-Architected"],
        }
        standards = []
        for key, values in standards_map.items():
            if key in audit_data.audit_type:
                standards.extend(values)
        if not standards:
            standards = ["Standards industriels"]

        methodology = Methodology(
            audit_type=audit_data.audit_type,
            standards=standards,
            tools=["Outils d'audit spécialisés"],
            phases=["Reconnaissance", "Analyse", "Exploitation", "Reporting"],
            approach=f"Approche méthodologique pour {audit_data.audit_type}"
        )
        state["sections"]["methodology"] = ReportSection(
            section_name="Méthodologie",
            content=f"Standards: {', '.join(standards)}",
            validated=True
        )
        state["metadata"]["methodology"] = methodology.model_dump()
        return state

    def generate_global_analysis(self, state: ReportState) -> ReportState:
        audit_data = state["audit_data"]
        total_findings = len(audit_data.findings)
        critical_weight = audit_data.critical_findings_count * 4
        high_weight = audit_data.high_findings_count * 3
        medium_weight = len([f for f in audit_data.findings if f.severity.value == "Medium"]) * 2
        low_weight = len([f for f in audit_data.findings if f.severity.value == "Low"]) * 1

        total_weight = critical_weight + high_weight + medium_weight + low_weight
        max_weight = total_findings * 4 if total_findings > 0 else 1
        security_score = max(0, 100 - (total_weight / max_weight * 100))

        risk_matrix = RiskMatrix(matrix={
            "Critical": {"Critical": audit_data.critical_findings_count, "High": 0, "Medium": 0, "Low": 0},
            "High": {"Critical": 0, "High": audit_data.high_findings_count, "Medium": 0, "Low": 0},
            "Medium": {"Critical": 0, "High": 0, "Medium": len([f for f in audit_data.findings if f.severity.value == "Medium"]), "Low": 0},
            "Low": {"Critical": 0, "High": 0, "Medium": 0, "Low": len([f for f in audit_data.findings if f.severity.value == "Low"])}
        })

        category_dist = {}
        for category, findings in audit_data.findings_by_category.items():
            percentage = (len(findings) / total_findings * 100) if total_findings > 0 else 0
            category_dist[category.value] = round(percentage, 1)

        analysis = GlobalAnalysis(
            security_score=round(security_score, 1),
            score_description=f"Score de sécurité: {round(security_score, 1)}/100",
            risk_matrix=risk_matrix,
            severity_distribution={
                "Critical": audit_data.critical_findings_count,
                "High": audit_data.high_findings_count,
                "Medium": len([f for f in audit_data.findings if f.severity.value == "Medium"]),
                "Low": len([f for f in audit_data.findings if f.severity.value == "Low"])
            },
            category_distribution=category_dist
        )
        state["sections"]["global_analysis"] = ReportSection(
            section_name="Analyse Globale",
            content=analysis.score_description
        )
        state["metadata"]["global_analysis"] = analysis.model_dump()
        return state

    def generate_findings(self, state: ReportState) -> ReportState:
        state["current_section"] = "findings"
        audit_data = state["audit_data"]
        enriched_findings = []
        for finding in audit_data.findings:
            enriched = self.creator.enrich_finding(finding, audit_data)
            enriched_findings.append(enriched)

        state["sections"]["findings"] = ReportSection(
            section_name="Findings Détaillés",
            content=f"{len(enriched_findings)} vulnérabilités identifiées"
        )
        state["metadata"]["findings"] = [f.model_dump() for f in enriched_findings]
        return state

    def generate_action_plan(self, state: ReportState) -> ReportState:
        state["current_section"] = "action_plan"
        findings_data = state["metadata"].get("findings", [])
        findings = [FindingDetail(**f) for f in findings_data]
        action_plan = self.creator.generate_action_plan(findings, state["audit_data"])
        state["sections"]["action_plan"] = ReportSection(
            section_name="Plan d'Action",
            content=action_plan.introduction
        )
        state["metadata"]["action_plan"] = action_plan.model_dump()
        return state

    def generate_conclusion(self, state: ReportState) -> ReportState:
        state["current_section"] = "conclusion"
        findings_data = state["metadata"].get("findings", [])
        findings = [FindingDetail(**f) for f in findings_data]
        conclusion = self.creator.generate_conclusion(state["audit_data"], findings)
        state["sections"]["conclusion"] = ReportSection(
            section_name="Conclusion",
            content=conclusion.summary
        )
        state["metadata"]["conclusion"] = conclusion.model_dump()
        return state

    def validate_sections(self, state: ReportState) -> ReportState:
        if not settings.enable_validation:
            for section in state["sections"].values():
                section.validated = True
            return state

        validation_results = []

        if "executive_summary" in state["metadata"]:
            summary = ExecutiveSummary(**state["metadata"]["executive_summary"])
            result = self.validator.validate_executive_summary(summary, len(state["audit_data"].findings))
            validation_results.append(result)

        findings_data = state["metadata"].get("findings", [])
        for finding_data in findings_data[:3]:
            finding = FindingDetail(**finding_data)
            result = self.validator.validate_finding(
                finding,
                f"{state['audit_data'].audit_type} - {state['audit_data'].get_metadata('sector', '')}"
            )
            validation_results.append(result)

        if "action_plan" in state["metadata"]:
            action_plan = ActionPlan(**state["metadata"]["action_plan"])
            result = self.validator.validate_action_plan(action_plan, len(state["audit_data"].findings))
            validation_results.append(result)

        if "conclusion" in state["metadata"]:
            conclusion = Conclusion(**state["metadata"]["conclusion"])
            result = self.validator.validate_conclusion(conclusion)
            validation_results.append(result)

        state["validation_results"] = validation_results
        return state

    def should_correct(self, state: ReportState) -> str:
        if state["iteration"] >= settings.max_iterations:
            return "done"

        needs_correction = any(
            vr.status == ValidationStatus.NEEDS_CORRECTION
            for vr in state["validation_results"]
        )

        if needs_correction:
            state["iteration"] += 1
            return "correct"

        return "done"

    def apply_corrections(self, state: ReportState) -> ReportState:
        for section in state["sections"].values():
            section.validated = True
        return state

    def assemble_report(self, state: ReportState) -> ReportState:
        try:
            cover = CoverPage(**state["metadata"]["cover_page"])
            summary = ExecutiveSummary(**state["metadata"]["executive_summary"])
            context = ContextScope(**state["metadata"]["context_scope"])
            methodology = Methodology(**state["metadata"]["methodology"])
            analysis = GlobalAnalysis(**state["metadata"]["global_analysis"])
            findings = [FindingDetail(**f) for f in state["metadata"]["findings"]]
            action_plan = ActionPlan(**state["metadata"]["action_plan"])
            conclusion = Conclusion(**state["metadata"]["conclusion"])

            full_report = FullReport(
                cover_page=cover,
                executive_summary=summary,
                context_scope=context,
                methodology=methodology,
                global_analysis=analysis,
                findings=findings,
                action_plan=action_plan,
                conclusion=conclusion,
                generation_timestamp=datetime.now().isoformat()
            )

            state["full_report"] = full_report
            state["metadata"]["end_time"] = datetime.now().isoformat()

        except Exception as e:
            state["error"] = str(e)

        return state
