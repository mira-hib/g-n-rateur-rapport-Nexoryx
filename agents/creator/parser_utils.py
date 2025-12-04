from typing import List, Optional
from models.audit_models import AuditFinding, SeverityLevel, PriorityLevel, CategoryType
from models.report_models import ActionItem, FindingDetail


class ParserUtils:
    """Utilitaires pour parser et formater les réponses LLM."""

    @staticmethod
    def extract_section(content: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extrait une section de texte entre deux marqueurs."""
        content_lower = content.lower()
        start_idx = content_lower.find(start_marker.lower())
        if start_idx == -1:
            return ""

        start_idx = content.find("\n", start_idx) + 1
        if end_marker:
            end_idx = content_lower.find(end_marker.lower(), start_idx)
            if end_idx != -1:
                return content[start_idx:end_idx].strip()
        return content[start_idx:].strip()

    @staticmethod
    def extract_recommendations(content: str) -> List[str]:
        """Extrait les recommandations d'un contenu LLM."""
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

    @staticmethod
    def extract_list_items(content: str, start_marker: str, end_marker: str) -> List[str]:
        """Extrait une liste d'items entre deux marqueurs."""
        section = ParserUtils.extract_section(content, start_marker, end_marker)
        items = []
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith(("-", "•", "*")):
                item = line.lstrip("-•* ").strip()
                if item:
                    items.append(item)
        return items

    @staticmethod
    def extract_introduction(content: str) -> str:
        """Extrait l'introduction d'un plan d'action."""
        lines = content.split("\n")
        intro_lines = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ["mesure", "priorité", "action", "tableau"]):
                break
            if line.strip() and not line.strip().startswith("#"):
                intro_lines.append(line.strip())
        return " ".join(intro_lines) if intro_lines else "Plan d'action priorisé pour la remédiation des vulnérabilités."

    @staticmethod
    def parse_actions(content: str, findings: List[FindingDetail]) -> List[ActionItem]:
        """Parse les actions du plan depuis le contenu LLM généré."""
        actions = []
        lines = content.split("\n")

        for line in lines:
            if "|" in line and not line.strip().startswith("#"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    try:
                        actions.append(ActionItem(
                            measure=parts[0],
                            priority=ParserUtils.parse_priority(parts[1]),
                            responsible=parts[2],
                            deadline=parts[3],
                            benefit=parts[4]
                        ))
                    except:
                        continue

        if not actions:
            for finding in findings[:10]:
                actions.append(ActionItem(
                    measure=f"Corriger: {finding.title}",
                    priority=finding.priority,
                    responsible=ParserUtils.suggest_responsible(finding.category),
                    deadline=ParserUtils.suggest_deadline(finding.priority),
                    benefit=f"Réduction du risque {finding.severity.value}",
                    related_finding=finding.title
                ))
        return actions

    @staticmethod
    def determine_priority(severity: SeverityLevel) -> PriorityLevel:
        """Détermine la priorité d'action selon la sévérité."""
        mapping = {
            SeverityLevel.CRITICAL: PriorityLevel.P0,
            SeverityLevel.HIGH: PriorityLevel.P1,
            SeverityLevel.MEDIUM: PriorityLevel.P2,
            SeverityLevel.LOW: PriorityLevel.P3
        }
        return mapping.get(severity, PriorityLevel.P2)

    @staticmethod
    def parse_priority(priority_str: str) -> PriorityLevel:
        """Parse une chaîne de priorité en enum PriorityLevel."""
        priority_str = priority_str.upper().strip()
        if "P0" in priority_str or "IMMÉDIAT" in priority_str:
            return PriorityLevel.P0
        elif "P1" in priority_str or "COURT" in priority_str:
            return PriorityLevel.P1
        elif "P2" in priority_str or "MOYEN" in priority_str:
            return PriorityLevel.P2
        else:
            return PriorityLevel.P3

    @staticmethod
    def suggest_responsible(category: CategoryType) -> str:
        """Suggère un responsable basé sur la catégorie de finding."""
        mapping = {
            "Network": "NetOps / RSSI",
            "AppSec": "Dev Lead / AppSec",
            "IAM": "IT Admin / IAM Team",
            "Cloud": "Cloud Ops / DevOps",
            "Governance": "RSSI / CISO",
            "Forensic": "Incident Response Team"
        }
        return mapping.get(str(category), "RSSI")

    @staticmethod
    def suggest_deadline(priority: PriorityLevel) -> str:
        """Suggère une deadline basée sur la priorité."""
        mapping = {
            PriorityLevel.P0: "1 semaine",
            PriorityLevel.P1: "1 mois",
            PriorityLevel.P2: "2-3 mois",
            PriorityLevel.P3: "3-6 mois"
        }
        return mapping.get(priority, "3 mois")

    @staticmethod
    def format_top_findings(findings: List[AuditFinding]) -> str:
        """Formate les top findings pour les prompts LLM."""
        return "\n".join([f"- [{f.severity.value}] {f.title}" for f in findings])

    @staticmethod
    def format_findings_for_action_plan(findings: List[FindingDetail]) -> str:
        """Formate les findings pour le prompt du plan d'action."""
        return "\n".join([
            f"{i+1}. [{f.priority.value}] {f.title} (Sévérité: {f.severity.value})"
            for i, f in enumerate(findings)
        ])