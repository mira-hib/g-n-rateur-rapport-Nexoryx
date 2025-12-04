from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from models.audit_models import AuditData, AuditFinding, SeverityLevel


class GenerationPrompts:
    """Prompts LLM pour la génération de contenu des rapports d'audit."""

    @staticmethod
    def resume_executif(audit_data: AuditData, top_findings_text: str) -> ChatPromptTemplate:
        """Génère le prompt pour créer le résumé exécutif."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un expert en cybersécurité qui rédige des résumés exécutifs pour des rapports d'audit destinés à la direction d'entreprise.

Ton objectif est de synthétiser les findings en un message clair, actionnable et compréhensible pour des non-techniques (CEO, CFO, COMEX).

Concentre-toi sur l'impact métier, les risques business et les recommandations prioritaires avec une timeline réaliste. Ton professionnel mais accessible."""),
            HumanMessage(content=f"""Génère un résumé exécutif pour cet audit:

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
3. Une timeline de remédiation réaliste

Sois concis mais impactant. Maximum 1 page.""")
        ])

    @staticmethod
    def enrichissement_vulnerabilite(audit_data: AuditData, finding: AuditFinding) -> ChatPromptTemplate:
        """Génère le prompt pour enrichir une vulnérabilité."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un expert en cybersécurité qui enrichit les findings d'audit avec des explications détaillées et des analyses d'impact métier.

Pour chaque vulnérabilité:
1. Expliquer techniquement le problème de manière détaillée mais accessible
2. Analyser l'impact business concret (pas juste technique)
3. Proposer des recommandations de correction détaillées et actionnables
4. Identifier la priorité d'action basée sur le risque

Ton audience inclut des techniques (RSSI, DevOps) et des non-techniques (Direction)."""),
            HumanMessage(content=f"""Enrichis cette vulnérabilité:

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

Format final: trois sections bien structurées.""")
        ])

    @staticmethod
    def plan_action(audit_data: AuditData, findings_text: str) -> ChatPromptTemplate:
        """Génère le prompt pour créer le plan d'action priorisé."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un consultant en cybersécurité qui crée des plans d'action concrets et actionnables pour la remédiation des vulnérabilités.

Ton plan doit:
- Prioriser les actions selon le risque (impact × likelihood)
- Être réaliste et implémentable
- Identifier des responsables logiques
- Proposer des deadlines appropriées
- Expliciter les bénéfices métier
- Identifier les dépendances"""),
            HumanMessage(content=f"""Génère un plan d'action priorisé pour cet audit:

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

Format: tableau clair.""")
        ])

    @staticmethod
    def conclusion(audit_data: AuditData, findings) -> ChatPromptTemplate:
        """Génère le prompt pour créer la conclusion du rapport."""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""Tu es un expert en cybersécurité qui rédige des conclusions de rapport d'audit de manière professionnelle et constructive.

La conclusion doit:
- Résumer le niveau de sécurité global
- Mettre en avant les points positifs
- Lister les axes d'amélioration majeurs
- Donner des recommandations stratégiques
- Proposer une vision de suivi futur"""),
            HumanMessage(content=f"""Génère une conclusion pour cet audit:

**Client:** {audit_data.client_name}
**Type d'audit:** {audit_data.audit_type}
**Secteur:** {audit_data.get_metadata('sector', 'Non spécifié')}

**Statistiques:**
- Total findings: {len(findings)}
- Critical: {len([f for f in findings if f.severity == SeverityLevel.CRITICAL])}
- High: {len([f for f in findings if f.severity == SeverityLevel.HIGH])}

Génère:
1. Récapitulatif du niveau de sécurité (1 paragraphe)
2. 3-5 points positifs
3. 3-5 axes d'amélioration majeurs
4. 3-5 recommandations stratégiques
5. Perspectives et suivi (1 paragraphe)

Format: maximum 1/2 page, ton professionnel et constructif.""")
        ])