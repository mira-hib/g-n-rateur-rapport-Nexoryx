from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from models.audit_models import *
from models.report_models import *


class AuditPrompts:

    @staticmethod
    def prompt_resume_executif(
        audit_data: AuditData, top_findings_text: str
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
Tu es un expert en cybersécurité qui rédige des résumés exécutifs
pour des rapports d'audit de sécurité destinés à la direction d'entreprise.

Ton objectif est de synthétiser les findings en un message clair, actionnable 
et compréhensible pour des non-techniques (CEO, CFO, COMEX).

Concentre-toi sur:
- L'impact métier des vulnérabilités
- Les risques business (financiers, réputationnels, légaux)
- Les recommandations prioritaires
- Une timeline réaliste

Utilise un ton professionnel mais accessible.
"""
                ),
                HumanMessage(
                    content=f"""
Génère un résumé exécutif pour cet audit:

**Client:** {audit_data.client_name}
**Type d'audit:** {audit_data.audit_type}
**Secteur:** {audit_data.get_metadata('sector', 'Non spécifié')}
**Taille entreprise:** {audit_data.get_metadata('company_size', 'Non spécifié')}

**Statistiques des findings:**
- Critical: {audit_data.critical_findings_count}
- High: {audit_data.high_findings_count}
- Medium: {len([f for f in audit_data.findings if f.severity == SeverityLevel.MEDIUM])}
- Low: {len([f for f in audit_data.findings if f.severity == SeverityLevel.LOW])}

**Principales vulnérabilités:**
{top_findings_text}

Génère:
1. Une vision synthétique (3–5 paragraphes) expliquant le niveau de sécurité global
2. 3–5 recommandations prioritaires concrètes
3. Une timeline de remédiation réaliste (ex: "Actions critiques sous 2 semaines, haute priorité sous 1 mois...")

Sois concis mais impactant. Maximum 1 page.
"""
                ),
            ]
        )

    @staticmethod
    def prompt_enrichissement_vulnerabilite(
        audit_data: AuditData, finding: AuditFinding
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
    Tu es un expert en cybersécurité qui enrichit les findings d'audit
    avec des explications détaillées et des analyses d'impact métier.
    Pour chaque vulnérabilité, tu dois:
    1. Expliquer techniquement le problème de manière détaillée mais accessible
    2. Analyser l'impact business concret (pas juste technique)
    3. Proposer des recommandations de correction détaillées et actionnables
    4. Identifier la priorité d'action basée sur le risque

    Ton audience inclut à la fois des techniques (RSSI, DevOps) 
    et des non-techniques (Direction).
    """
                ),
                HumanMessage(
                    content=f"""
    Enrichis cette vulnérabilité:

    **Titre:** {finding.title}
    **Catégorie:** {finding.category.value}
    **Sévérité:** {finding.severity.value}
    **Description de base:** {finding.description}
    **Preuve:** {finding.evidence}
    **Recommandation de base:** {finding.recommendation}

    **Contexte de l'audit:**
    - Client: {audit_data.client_name}
    - Type: {audit_data.audit_type}
    - Secteur: {audit_data.get_metadata('sector', 'Non spécifié')}

    Génère:
    1. Description enrichie (2-3 paragraphes)
    2. Impact métier (1-2 paragraphes)
    3. Recommandation enrichie (plusieurs paragraphes)

    Format final: trois sections bien structurées.
    """
                ),
            ]
        )

    @staticmethod
    def prompt_plan_action(
        audit_data: AuditData, findings_text: str
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
            Tu es un consultant en cybersécurité qui crée des plans d'action
            concrets et actionnables pour la remédiation des vulnérabilités.

            Ton plan doit:
            - Prioriser les actions selon le risque (impact × likelihood)
            - Être réaliste et implémentable
            - Identifier des responsables logiques
            - Proposer des deadlines appropriées
            - Expliciter les bénéfices métier
            - Identifier les dépendances
            """
                ),
                HumanMessage(
                    content=f"""
            Génère un plan d'action priorisé pour cet audit:

            **Client:** {audit_data.client_name}
            **Type d'audit:** {audit_data.audit_type}
            **Secteur:** {audit_data.get_metadata('sector', 'Non spécifié')}

            **Findings à adresser:**
            {findings_text}

            Génère:
            1. Une introduction (1 paragraphe)
            2. 10–15 actions concrètes priorisées (P0, P1, P2, P3)
            3. Pour chaque action:
            - Mesure
            - Priorité
            - Responsable
            - Deadline
            - Bénéfice métier
            4. Dépendances si nécessaire

            Format: tableau clair.
            """
                ),
            ]
        )

    @staticmethod
    def prompt_conclusion(
        audit_data: AuditData, findings: AuditFinding
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
            Tu es un expert en cybersécurité qui rédige des conclusions de rapport
            d'audit de manière professionnelle et constructive.

            La conclusion doit:
            - Résumer le niveau de sécurité global
            - Mettre en avant les points positifs
            - Lister les axes d'amélioration majeurs
            - Donner des recommandations stratégiques
            - Proposer une vision de suivi futur
            """
                ),
                HumanMessage(
                    content=f"""
            Génère une conclusion pour cet audit:

            **Client:** {audit_data.client_name}
            **Type d'audit:** {audit_data.audit_type}
            **Secteur:** {audit_data.get_metadata('sector', 'Non spécifié')}

            **Statistiques:**
            - Total findings : {len(findings)}
            - Critical : {len([f for f in findings if f.severity == SeverityLevel.CRITICAL])}
            - High : {len([f for f in findings if f.severity == SeverityLevel.HIGH])}

            Génère:
            1. Récapitulatif du niveau de sécurité (1 paragraphe)
            2. 3-5 points positifs
            3. 3-5 axes d'amélioration majeurs
            4. 3-5 recommandations stratégiques
            5. Perspectives et suivi (1 paragraphe)

            Format : maximum 1/2 page, ton professionnel et constructif.
            """
                ),
            ]
        )

    @staticmethod
    def prompt_validate_resume(
        summary: ExecutiveSummary, total_findings: int
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""Tu es un auditeur senior qui vérifie la qualité des résumés exécutifs
            de rapports d'audit de cybersécurité.

            Tu dois vérifier:
            1. **Cohérence**: Les chiffres correspondent-ils? Le niveau de risque est-il aligné avec les statistiques?
            2. **Complétude**: Toutes les informations clés sont-elles présentes?
            3. **Qualité**: Le texte est-il clair, professionnel et sans jargon excessif?
            4. **Actionabilité**: Les recommandations sont-elles concrètes et implémentables?
            5. **Longueur**: Le résumé est-il approprié (ni trop court ni trop long)?

            Donne un score de 0 à 100, liste les problèmes trouvés, et suggère des améliorations."""
                ),
                HumanMessage(
                    content=f"""Valide ce résumé exécutif:

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

            Analyse critique:
            1. Identifie tous les problèmes (incohérences, informations manquantes, erreurs)
            2. Note la qualité rédactionnelle (clarté, professionnalisme)
            3. Évalue l'actionabilité des recommandations
            4. Donne un score global de 0 à 100
            5. Suggère 2-3 améliorations concrètes

            Format ta réponse:
            SCORE: [0-100]
            PROBLÈMES:
            - [liste des problèmes]
            SUGGESTIONS:
            - [liste des suggestions]"""
                ),
            ]
        )

    @staticmethod
    def prompt_validate_finding(
        finding: AuditFinding, context: str
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""Tu es un expert en cybersécurité qui vérifie la qualité des findingsdans les rapports d'audit.

            Tu dois vérifier:
            1. **Précision technique**: La description est-elle techniquement correcte et précise?
            2. **Complétude**: Toutes les informations nécessaires sont-elles présentes?
            3. **Impact métier**: L'analyse d'impact est-elle pertinente et réaliste?
            4. **Recommandations**: Les recommandations sont-elles actionnables et détaillées?
            5. **Cohérence**: La sévérité correspond-elle à la description et à l'impact?
            6. **Qualité**: Le texte est-il clair et professionnel?

            Donne un score de 0 à 100, liste les problèmes, et suggère des améliorations."""
                ),
                HumanMessage(
                    content=f"""Valide ce finding:

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

            Analyse critique:
            1. Vérifie la précision technique
            2. Évalue la pertinence de l'impact métier
            3. Juge l'actionabilité des recommandations
            4. Vérifie la cohérence sévérité/description/impact/priorité
            5. Donne un score de 0 à 100
            6. Liste les problèmes et suggestions

            Format:
            SCORE: [0-100]
            PROBLÈMES:
            - [liste]
            SUGGESTIONS:
            - [liste]"""
                ),
            ]
        )

    @staticmethod
    def prompt_validate_plan_action(
        action_plan: ActionPlan, findings_count: int, format_actions_for_validation: str
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un consultant qui vérifie la qualité des plans d'action
            de remédiation de cybersécurité.

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
            {format_actions_for_validation}

            **Dépendances:**
            {action_plan.dependencies or "Non spécifiées"}

            Analyse:
            1. Vérifie que le nombre d'actions est approprié
            2. Évalue la pertinence des priorités (P0/P1/P2/P3)
            3. Juge la qualité des responsables suggérés
            4. Vérifie le réalisme des deadlines
            5. Évalue la clarté des bénéfices
            6. Donne un score de 0 à 100

            Format:
            SCORE: [0-100]
            PROBLÈMES:
            - [liste]
            SUGGESTIONS:
            - [liste]""")
        ])

    @staticmethod
    def prompt_validate_conclusion(
        conclusion: Conclusion, context: str
    ) -> ChatPromptTemplate:
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

            Analyse:
            1. Évalue l'équilibre positif/amélioration
            2. Vérifie la pertinence des recommandations stratégiques
            3. Juge le réalisme des prochaines étapes
            4. Donne un score de 0 à 100

            Format:
            SCORE: [0-100]
            PROBLÈMES:
            - [liste]
            SUGGESTIONS:
            - [liste]""")
        ])

    @staticmethod
    def prompt_validate_full_report(
        sections: Dict[str, ReportSection], format_sections_for_coherence_check
    ) -> ChatPromptTemplate:
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
            {format_sections_for_coherence_check}

            Vérifie:
            1. La cohérence des statistiques mentionnées
            2. L'absence de contradictions entre sections
            3. La présence de toutes les sections essentielles
            4. L'uniformité du ton
            5. La logique narrative

            Format:
            SCORE: [0-100]
            PROBLÈMES:
            - [liste]
            SUGGESTIONS:
            - [liste]""")
        ])
