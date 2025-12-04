from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from models.report_models import ExecutiveSummary, FindingDetail, ActionPlan, Conclusion, ReportSection


class ValidationPrompts:
    """Prompts LLM pour la validation de qualité des sections de rapport."""

    @staticmethod
    def validate_resume(summary: ExecutiveSummary, total_findings: int) -> ChatPromptTemplate:
        """Génère le prompt pour valider le résumé exécutif."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un auditeur senior qui vérifie la qualité des résumés exécutifs de rapports d'audit de cybersécurité.

Tu dois vérifier:
1. **Cohérence**: Les chiffres correspondent-ils? Le niveau de risque est-il aligné avec les statistiques?
2. **Complétude**: Toutes les informations clés sont-elles présentes?
3. **Qualité**: Le texte est-il clair, professionnel et sans jargon excessif?
4. **Actionabilité**: Les recommandations sont-elles concrètes et implémentables?
5. **Longueur**: Le résumé est-il approprié?

Donne un score de 0 à 100, liste les problèmes trouvés, et suggère des améliorations."""),
            HumanMessage(content=f"""Valide ce résumé exécutif:

**Overview:**
{summary.overview}

**Niveau de risque global:** {summary.global_risk_level.value}

**Statistiques:**
- Critical: {summary.critical_count}
- High: {summary.high_count}
- Medium: {summary.medium_count}
- Low: {summary.low_count}
- Total attendu: {total_findings}

**Recommandations prioritaires:**
{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(summary.top_recommendations))}

**Timeline de remédiation:**
{summary.remediation_timeline}

Analyse critique et format ta réponse:
SCORE: [0-100]
PROBLÈMES:
- [liste des problèmes]
SUGGESTIONS:
- [liste des suggestions]""")
        ])

    @staticmethod
    def validate_finding(finding: FindingDetail, context: str) -> ChatPromptTemplate:
        """Génère le prompt pour valider un finding enrichi."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un expert en cybersécurité qui vérifie la qualité des findings dans les rapports d'audit.

Tu dois vérifier:
1. **Précision technique**: La description est-elle techniquement correcte et précise?
2. **Complétude**: Toutes les informations nécessaires sont-elles présentes?
3. **Impact métier**: L'analyse d'impact est-elle pertinente et réaliste?
4. **Recommandations**: Les recommandations sont-elles actionnables et détaillées?
5. **Cohérence**: La sévérité correspond-elle à la description et à l'impact?
6. **Qualité**: Le texte est-il clair et professionnel?

Donne un score de 0 à 100, liste les problèmes, et suggère des améliorations."""),
            HumanMessage(content=f"""Valide ce finding:

**Titre:** {finding.title}
**Catégorie:** {finding.category.value}
**Sévérité:** {finding.severity.value}
**Priorité:** {finding.priority.value}

**Description enrichie:**
{finding.enriched_description}

**Impact métier:**
{finding.business_impact}

**Preuve:**
{finding.evidence}

**Recommandation enrichie:**
{finding.enriched_recommendation}

**Contexte:** {context}

Analyse critique et format:
SCORE: [0-100]
PROBLÈMES:
- [liste]
SUGGESTIONS:
- [liste]""")
        ])

    @staticmethod
    def validate_plan_action(action_plan: ActionPlan, findings_count: int, format_actions: str) -> ChatPromptTemplate:
        """Génère le prompt pour valider le plan d'action."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un consultant qui vérifie la qualité des plans d'action de remédiation de cybersécurité.

Tu dois vérifier:
1. **Complétude**: Le plan couvre-t-il tous les findings majeurs?
2. **Priorisation**: Les priorités sont-elles logiques et cohérentes?
3. **Actionabilité**: Les mesures sont-elles concrètes et implémentables?
4. **Responsables**: Les responsables suggérés sont-ils pertinents?
5. **Deadlines**: Les délais sont-ils réalistes?
6. **Bénéfices**: Les bénéfices sont-ils clairement explicités?

Donne un score de 0 à 100 et des suggestions."""),
            HumanMessage(content=f"""Valide ce plan d'action:

**Introduction:**
{action_plan.introduction}

**Nombre d'actions:** {len(action_plan.actions)}
**Nombre de findings à adresser:** {findings_count}

**Actions:**
{format_actions}

**Dépendances:**
{action_plan.dependencies or "Non spécifiées"}

Analyse et format:
SCORE: [0-100]
PROBLÈMES:
- [liste]
SUGGESTIONS:
- [liste]""")
        ])

    @staticmethod
    def validate_conclusion(conclusion: Conclusion, context: str) -> ChatPromptTemplate:
        """Génère le prompt pour valider la conclusion."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un auditeur qui vérifie la qualité des conclusions de rapports d'audit de cybersécurité.

Tu dois vérifier:
1. **Équilibre**: La conclusion est-elle équilibrée (positif + amélioration)?
2. **Cohérence**: Est-elle cohérente avec le reste du rapport?
3. **Constructivité**: Le ton est-il professionnel et constructif?
4. **Complétude**: Tous les éléments sont-ils présents?
5. **Perspectives**: Les prochaines étapes sont-elles claires?

Donne un score de 0 à 100 et des suggestions."""),
            HumanMessage(content=f"""Valide cette conclusion:

**Récapitulatif:**
{conclusion.summary}

**Points positifs ({len(conclusion.positive_points)}):**
{chr(10).join(f'- {p}' for p in conclusion.positive_points)}

**Axes d'amélioration ({len(conclusion.improvement_areas)}):**
{chr(10).join(f'- {a}' for a in conclusion.improvement_areas)}

**Recommandations stratégiques ({len(conclusion.strategic_recommendations)}):**
{chr(10).join(f'- {r}' for r in conclusion.strategic_recommendations)}

**Prochaines étapes:**
{conclusion.next_steps}

**Contexte:** {context}

Analyse et format:
SCORE: [0-100]
PROBLÈMES:
- [liste]
SUGGESTIONS:
- [liste]""")
        ])

    @staticmethod
    def validate_full_report(sections: Dict[str, ReportSection], format_sections: str) -> ChatPromptTemplate:
        """Génère le prompt pour valider la cohérence globale du rapport."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un auditeur senior qui vérifie la cohérence globale d'un rapport d'audit de cybersécurité complet.

Tu dois vérifier:
1. **Cohérence inter-sections**: Les sections se complètent-elles sans contradiction?
2. **Fil narratif**: Le rapport a-t-il un fil conducteur logique?
3. **Statistiques**: Les chiffres sont-ils cohérents d'une section à l'autre?
4. **Ton**: Le ton est-il uniforme tout au long du rapport?
5. **Complétude**: Toutes les sections essentielles sont-elles présentes?

Donne un score de 0 à 100 et des recommandations."""),
            HumanMessage(content=f"""Analyse la cohérence de ce rapport:

**Sections présentes ({len(sections)}):**
{chr(10).join(f'- {name}' for name in sections.keys())}

**Extraits de chaque section:**
{format_sections}

Vérifie la cohérence des statistiques, l'absence de contradictions, la présence de toutes les sections essentielles, l'uniformité du ton et la logique narrative.

Format:
SCORE: [0-100]
PROBLÈMES:
- [liste]
SUGGESTIONS:
- [liste]""")
        ])