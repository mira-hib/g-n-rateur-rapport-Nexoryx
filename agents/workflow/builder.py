from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from models.state_models import ReportState
from config.settings import settings


class WorkflowBuilder:
    """Constructeur du graphe LangGraph pour l'orchestration du workflow de génération."""

    @staticmethod
    def build_graph(nodes) -> StateGraph:
        workflow = StateGraph(ReportState)

        workflow.add_node("initialize", nodes.initialize_state)
        workflow.add_node("generate_cover", nodes.generate_cover_page)
        workflow.add_node("generate_executive_summary", nodes.generate_executive_summary)
        workflow.add_node("generate_context", nodes.generate_context_scope)
        workflow.add_node("generate_methodology", nodes.generate_methodology)
        workflow.add_node("generate_global_analysis", nodes.generate_global_analysis)
        workflow.add_node("generate_findings", nodes.generate_findings)
        workflow.add_node("generate_action_plan", nodes.generate_action_plan)
        workflow.add_node("generate_conclusion", nodes.generate_conclusion)
        workflow.add_node("validate_sections", nodes.validate_sections)
        workflow.add_node("apply_corrections", nodes.apply_corrections)
        workflow.add_node("assemble_report", nodes.assemble_report)

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

        workflow.add_conditional_edges(
            "validate_sections",
            nodes.should_correct,
            {"correct": "apply_corrections", "done": "assemble_report"}
        )
        workflow.add_edge("apply_corrections", "validate_sections")
        workflow.add_edge("assemble_report", END)

        return workflow.compile(checkpointer=MemorySaver() if settings.checkpoint_enabled else None)
