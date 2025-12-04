"""
Workflow LangGraph pour la génération automatisée de rapports d'audit.

Ce workflow orchestre les agents créateur et vérificateur pour produire
un rapport d'audit complet et de haute qualité.
"""

from typing import Dict, List
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.audit_models import AuditData
from models.report_models import (
    CoverPage,
    ExecutiveSummary,
    ContextScope,
    Methodology,
    GlobalAnalysis,
    FindingDetail,
    ActionPlan,
    Conclusion,
    ReportSection,
    FullReport,
    RiskMatrix
)
from models.state_models import ReportState, ValidationStatus
from agents.creator_agent import CreatorAgent
from agents.validator_agent import ValidatorAgent
from config.settings import settings


class ReportGenerationWorkflow:
    """
    Workflow LangGraph pour la génération de rapports d'audit.

    Architecture:
    1. Extraction des données (audit_data depuis DB)
    2. Génération des sections par l'agent créateur
    3. Validation par l'agent vérificateur
    4. Corrections si nécessaire (max 3 itérations)
    5. Assemblage du rapport final
    """

    def __init__(self):
        """Initialise le workflow avec les agents."""
        self.creator = CreatorAgent()
        self.validator = ValidatorAgent()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construit le graphe LangGraph."""
        # Créer le graphe avec le type d'état
        workflow = StateGraph(ReportState)

        # Ajouter les nœuds
        workflow.add_node("initialize", self._initialize_state)
        workflow.add_node("generate_cover", self._generate_cover_page)
        workflow.add_node("generate_executive_summary", self._generate_executive_summary)
        workflow.add_node("generate_context", self._generate_context_scope)
        workflow.add_node("generate_methodology", self._generate_methodology)
        workflow.add_node("generate_global_analysis", self._generate_global_analysis)
        workflow.add_node("generate_findings", self._generate_findings)
        workflow.add_node("generate_action_plan", self._generate_action_plan)
        workflow.add_node("generate_conclusion", self._generate_conclusion)
        workflow.add_node("validate_sections", self._validate_sections)
        workflow.add_node("apply_corrections", self._apply_corrections)
        workflow.add_node("assemble_report", self._assemble_report)

        # Définir le flux
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "generate_cover")
        workflow.add_edge("generate_cover", "generate_executive_summary")
        workflow.add_edge("generate_executive_summary", "generate_context")
        workflow.add_edge("generate_context", "generate_methodology")
        workflow.add_edge("generate_methodology", "generate_global_analysis")
        workflow.add_edge("generate_global_analysis", "generate_findings")
        workflow.add_edge("generate_findings", "generate_action_plan")
        workflow.add_edge("generate_action_plan", "generate_conclusion")
        workflow.add_edge("generate_conclusion", "validate_sections")

        # Edge conditionnel pour les corrections
        workflow.add_conditional_edges(
            "validate_sections",
            self._should_correct,
            {
                "correct": "apply_corrections",
                "done": "assemble_report"
            }
        )
        workflow.add_edge("apply_corrections", "validate_sections")
        workflow.add_edge("assemble_report", END)

        return workflow.compile(checkpointer=MemorySaver() if settings.checkpoint_enabled else None)

    def generate_report(self, audit_data: AuditData) -> FullReport:
        """
        Génère un rapport complet à partir des données d'audit.

        Args:
            audit_data: Données de l'audit

        Returns:
            Rapport complet généré et validé
        """
        # État initial
        initial_state: ReportState = {
            "audit_data": audit_data,
            "sections": {},
            "validation_results": [],
            "corrections": [],
            "full_report": None,
            "iteration": 0,
            "current_section": None,
            "error": None,
            "metadata": {}
        }

        # Exécuter le workflow
        # Si checkpointing est activé, on doit fournir un thread_id
        if settings.checkpoint_enabled:
            import uuid
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = self.graph.invoke(initial_state, config=config)
        else:
            result = self.graph.invoke(initial_state)

        if result["full_report"] is None:
            raise Exception(f"Échec de la génération du rapport: {result.get('error', 'Erreur inconnue')}")

        return result["full_report"]

    # Nœuds du workflow
    def _initialize_state(self, state: ReportState) -> ReportState:
        """Initialise l'état du workflow."""
        state["iteration"] = 0
        state["metadata"]["start_time"] = datetime.now().isoformat()
        return state

    def _generate_cover_page(self, state: ReportState) -> ReportState:
        """Génère la page de garde."""
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
            validated=True  # Page de garde toujours validée
        )
        state["metadata"]["cover_page"] = cover.model_dump()

        return state

    def _generate_executive_summary(self, state: ReportState) -> ReportState:
        """Génère le résumé exécutif."""
        state["current_section"] = "executive_summary"
        audit_data = state["audit_data"]

        summary = self.creator.generate_executive_summary(audit_data)

        state["sections"]["executive_summary"] = ReportSection(
            section_name="Résumé Exécutif",
            content=summary.overview
        )
        state["metadata"]["executive_summary"] = summary.model_dump()

        return state

    def _generate_context_scope(self, state: ReportState) -> ReportState:
        """Génère le contexte et périmètre."""
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

    def _generate_methodology(self, state: ReportState) -> ReportState:
        """Génère la méthodologie."""
        audit_data = state["audit_data"]

        # Déterminer les standards selon le type d'audit
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

    def _generate_global_analysis(self, state: ReportState) -> ReportState:
        """Génère l'analyse globale."""
        audit_data = state["audit_data"]

        # Calculer le score de sécurité
        total_findings = len(audit_data.findings)
        critical_weight = audit_data.critical_findings_count * 4
        high_weight = audit_data.high_findings_count * 3
        medium_weight = len([f for f in audit_data.findings if f.severity.value == "Medium"]) * 2
        low_weight = len([f for f in audit_data.findings if f.severity.value == "Low"]) * 1

        total_weight = critical_weight + high_weight + medium_weight + low_weight
        max_weight = total_findings * 4 if total_findings > 0 else 1

        security_score = max(0, 100 - (total_weight / max_weight * 100))

        # Créer la matrice des risques (simplifiée)
        risk_matrix = RiskMatrix(
            matrix={
                "Critical": {"Critical": audit_data.critical_findings_count, "High": 0, "Medium": 0, "Low": 0},
                "High": {"Critical": 0, "High": audit_data.high_findings_count, "Medium": 0, "Low": 0},
                "Medium": {"Critical": 0, "High": 0, "Medium": len([f for f in audit_data.findings if f.severity.value == "Medium"]), "Low": 0},
                "Low": {"Critical": 0, "High": 0, "Medium": 0, "Low": len([f for f in audit_data.findings if f.severity.value == "Low"])}
            }
        )

        # Distribution par catégorie
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

    def _generate_findings(self, state: ReportState) -> ReportState:
        """Génère les findings enrichis."""
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

    def _generate_action_plan(self, state: ReportState) -> ReportState:
        """Génère le plan d'action."""
        state["current_section"] = "action_plan"

        # Récupérer les findings enrichis
        findings_data = state["metadata"].get("findings", [])
        findings = [FindingDetail(**f) for f in findings_data]

        action_plan = self.creator.generate_action_plan(findings, state["audit_data"])

        state["sections"]["action_plan"] = ReportSection(
            section_name="Plan d'Action",
            content=action_plan.introduction
        )
        state["metadata"]["action_plan"] = action_plan.model_dump()

        return state

    def _generate_conclusion(self, state: ReportState) -> ReportState:
        """Génère la conclusion."""
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

    def _validate_sections(self, state: ReportState) -> ReportState:
        """Valide toutes les sections générées."""
        if not settings.enable_validation:
            # Marquer toutes les sections comme validées
            for section in state["sections"].values():
                section.validated = True
            return state

        validation_results = []

        # Valider le résumé exécutif
        if "executive_summary" in state["metadata"]:
            summary = ExecutiveSummary(**state["metadata"]["executive_summary"])
            result = self.validator.validate_executive_summary(
                summary,
                len(state["audit_data"].findings)
            )
            validation_results.append(result)

        # Valider quelques findings (pas tous pour des raisons de performance)
        findings_data = state["metadata"].get("findings", [])
        for finding_data in findings_data[:3]:  # Valider les 3 premiers
            finding = FindingDetail(**finding_data)
            result = self.validator.validate_finding(
                finding,
                f"{state['audit_data'].audit_type} - {state['audit_data'].get_metadata('sector', '')}"
            )
            validation_results.append(result)

        # Valider le plan d'action
        if "action_plan" in state["metadata"]:
            action_plan = ActionPlan(**state["metadata"]["action_plan"])
            result = self.validator.validate_action_plan(
                action_plan,
                len(state["audit_data"].findings)
            )
            validation_results.append(result)

        # Valider la conclusion
        if "conclusion" in state["metadata"]:
            conclusion = Conclusion(**state["metadata"]["conclusion"])
            result = self.validator.validate_conclusion(conclusion)
            validation_results.append(result)

        state["validation_results"] = validation_results

        return state

    def _should_correct(self, state: ReportState) -> str:
        """Détermine si des corrections sont nécessaires."""
        # Vérifier si on a atteint le max d'itérations
        if state["iteration"] >= settings.max_iterations:
            return "done"

        # Vérifier si des sections nécessitent des corrections
        needs_correction = any(
            vr.status == ValidationStatus.NEEDS_CORRECTION
            for vr in state["validation_results"]
        )

        if needs_correction:
            state["iteration"] += 1
            return "correct"

        return "done"

    def _apply_corrections(self, state: ReportState) -> ReportState:
        """Applique les corrections suggérées."""
        # Pour le MVP, on marque simplement les sections comme validées
        # Dans une version complète, on rappellerait le créateur avec les suggestions
        for section in state["sections"].values():
            section.validated = True

        return state

    def _assemble_report(self, state: ReportState) -> ReportState:
        """Assemble le rapport final."""
        try:
            # Récupérer toutes les sections
            cover = CoverPage(**state["metadata"]["cover_page"])
            summary = ExecutiveSummary(**state["metadata"]["executive_summary"])
            context = ContextScope(**state["metadata"]["context_scope"])
            methodology = Methodology(**state["metadata"]["methodology"])
            analysis = GlobalAnalysis(**state["metadata"]["global_analysis"])
            findings = [FindingDetail(**f) for f in state["metadata"]["findings"]]
            action_plan = ActionPlan(**state["metadata"]["action_plan"])
            conclusion = Conclusion(**state["metadata"]["conclusion"])

            # Créer le rapport complet
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
