import re
from typing import List


class ValidationParser:
    """Utilitaires pour parser les réponses de validation LLM."""

    @staticmethod
    def extract_score(content: str) -> float:
        """Extrait le score numérique d'une réponse de validation."""
        match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", content, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 75.0

    @staticmethod
    def extract_list(content: str, start_marker: str, end_marker: str | None) -> List[str]:
        """Extrait une liste d'items entre deux marqueurs (PROBLÈMES:, SUGGESTIONS:)."""
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

    @staticmethod
    def format_actions_for_validation(actions: List) -> str:
        """Formate les actions pour les prompts de validation."""
        return "\n".join([
            f"{i+1}. [{action.priority.value}] {action.measure} | "
            f"{action.responsible} | {action.deadline} | {action.benefit}"
            for i, action in enumerate(actions[:10])
        ])

    @staticmethod
    def format_sections_for_coherence_check(sections: dict) -> str:
        """Formate les sections pour la vérification de cohérence globale."""
        formatted = []
        for name, section in list(sections.items())[:5]:
            preview = section.content[:200] + "..." if len(section.content) > 200 else section.content
            formatted.append(f"**{name}:**\n{preview}\n")
        return "\n".join(formatted)