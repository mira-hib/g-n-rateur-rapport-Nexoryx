import uuid
from models.audit_models import AuditData
from models.report_models import FullReport
from models.state_models import ReportState
from agents.creator import CreatorAgent
from agents.validator import ValidatorAgent
from agents.workflow.nodes import WorkflowNodes
from agents.workflow.builder import WorkflowBuilder
from config.settings import settings


class ReportGenerationWorkflow:
    """Workflow LangGraph orchestrant la génération automatisée de rapports d'audit."""

    def __init__(self):
        self.creator = CreatorAgent()
        self.validator = ValidatorAgent()
        self.nodes = WorkflowNodes(self.creator, self.validator)
        self.graph = WorkflowBuilder.build_graph(self.nodes)

    def generate_report(self, audit_data: AuditData) -> FullReport:
        """Génère un rapport complet enrichi par LLM à partir des données d'audit."""
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

        if settings.checkpoint_enabled:
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = self.graph.invoke(initial_state, config=config)
        else:
            result = self.graph.invoke(initial_state)

        if result["full_report"] is None:
            raise Exception(f"Échec de la génération du rapport: {result.get('error', 'Erreur inconnue')}")

        return result["full_report"]


__all__ = ["ReportGenerationWorkflow"]
