# OFFRE TECHNIQUE - Générateur Automatisé de Rapports d'Audit Nexoryx

## 1. Contexte et Problématique

### Problème identifié
Les clients de Nexoryx se plaignent de la qualité des rapports d'audit de cybersécurité fournis, notamment :
- Manque de cohérence dans la structure
- Descriptions techniques insuffisamment détaillées
- Absence de contextualisation métier
- Plans d'action peu exploitables
- Temps de production important

### Solution proposée
Un système intelligent de génération automatisée de rapports utilisant :
- Intelligence Artificielle pour enrichir le contenu
- Architecture multi-agents pour assurer la qualité
- Workflow orchestré pour garantir la cohérence

---

## 2. Architecture Technique

### 2.1 Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTÈME DE GÉNÉRATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────────────────┐          │
│  │   Base de   │─────▶│   Extracteur de données  │          │
│  │   Données   │      └──────────┬───────────────┘          │
│  │  (SQLite)   │                 │                           │
│  └─────────────┘                 ▼                           │
│                        ┌─────────────────────┐               │
│                        │  LANGGRAPH WORKFLOW │               │
│                        │  (Orchestrateur)    │               │
│                        └──────────┬──────────┘               │
│                                   │                           │
│                    ┌──────────────┴───────────────┐          │
│                    │                                │          │
│                    ▼                                ▼          │
│         ┌──────────────────┐            ┌──────────────────┐ │
│         │  AGENT CRÉATEUR  │◀──────────▶│ AGENT VÉRIFICATEUR│ │
│         │                  │            │                  │ │
│         │ - Génère sections│            │ - Valide qualité │ │
│         │ - Enrichit IA    │            │ - Vérifie cohér. │ │
│         │ - Contextualise  │            │ - Corrige erreurs│ │
│         └────────┬─────────┘            └──────────┬───────┘ │
│                  │                                  │          │
│                  └───────────┬──────────────────────┘          │
│                              │                                 │
│                              ▼                                 │
│                  ┌───────────────────────┐                    │
│                  │ Générateur de Rapport │                    │
│                  │    (PDF/DOCX/HTML)    │                    │
│                  └───────────┬───────────┘                    │
│                              │                                 │
│                              ▼                                 │
│                  ┌───────────────────────┐                    │
│                  │   RAPPORT FINAL       │                    │
│                  └───────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Composants Détaillés

#### Base de Données (SQLite)
- **Tables existantes** :
  - `audits` : Informations générales (client, type, date, auditeur, périmètre)
  - `audit_findings` : Vulnérabilités identifiées (titre, sévérité, preuves, recommandations)
  - `audit_metadata` : Métadonnées contextuelles (secteur, taille, risque global)

#### Orchestrateur LangGraph
- **Rôle** : Coordonner le workflow de génération
- **Composants** :
  - State Management : Gestion de l'état du rapport en cours
  - Node Routing : Routage entre agents
  - Conditional Edges : Boucles de validation/correction
  - Checkpointing : Sauvegarde intermédiaire

#### Agent Créateur
- **Modèle** : GPT-4 / Claude 3.5 Sonnet
- **Responsabilités** :
  - Générer le contenu de chaque section
  - Enrichir les descriptions techniques
  - Contextualiser pour le métier du client
  - Créer les analyses et recommandations
  - Générer le plan d'action priorisé

#### Agent Vérificateur
- **Modèle** : GPT-4 / Claude 3.5 Sonnet
- **Responsabilités** :
  - Valider la cohérence du contenu
  - Vérifier la complétude des sections
  - Détecter les incohérences techniques
  - Évaluer la qualité rédactionnelle
  - Suggérer des corrections

---

## 3. Choix Technologiques

### 3.1 Stack Technique

| Composant | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| **Backend** | Python | 3.11+ | Écosystème IA riche, typage statique |
| **Framework IA** | LangGraph | 0.2+ | Orchestration multi-agents, workflow complexe |
| **LLM Provider** | OpenAI/Anthropic | GPT-4/Claude 3.5 | Qualité de génération, raisonnement |
| **Base de données** | SQLite | 3.x | Simplicité, portabilité, pas de serveur |
| **Validation/Typage** | Pydantic | 2.x | Validation runtime, génération de schémas |
| **Génération PDF** | ReportLab | 4.x | Contrôle total, personnalisation |
| **Génération DOCX** | python-docx | 1.x | Format éditable, compatibilité Office |
| **Templating** | Jinja2 | 3.x | Flexibilité, lisibilité |
| **Interface** | Streamlit | 1.x | Rapidité de développement, interactivité |

### 3.2 Justification des Choix

#### Pourquoi LangGraph ?
1. **Workflows complexes** : Gestion des boucles de validation/correction
2. **Multi-agents** : Orchestration naturelle de plusieurs agents
3. **State persistence** : Sauvegarde automatique de l'état
4. **Conditional routing** : Décisions basées sur la qualité du contenu
5. **Human-in-the-loop** : Possibilité de validation manuelle

#### Pourquoi Pydantic ?
1. **Type safety** : Validation des données à runtime
2. **Auto-documentation** : Génération de schémas JSON
3. **IDE support** : Autocomplétion et détection d'erreurs
4. **Performances** : Validation rapide en Rust
5. **Intégration LangChain** : Support natif

#### Pourquoi un système multi-agents ?
1. **Séparation des responsabilités** : Créateur vs Vérificateur
2. **Qualité accrue** : Double vérification automatique
3. **Spécialisation** : Prompts optimisés par rôle
4. **Scalabilité** : Ajout facile de nouveaux agents
5. **Traçabilité** : Historique des modifications

---

## 4. Workflow de Génération Automatisée

### 4.1 Diagramme de Flux

```
[DÉBUT]
   │
   ▼
┌────────────────────┐
│ 1. Extraction DB   │ ← Récupération audit + findings + metadata
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 2. Initialisation  │ ← Création de l'état initial du rapport
│    State LangGraph │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 3. Génération      │ ← AGENT CRÉATEUR
│    Section par     │   • Page de garde
│    Section         │   • Résumé exécutif
│                    │   • Contexte & Périmètre
│                    │   • Méthodologie
│                    │   • Analyse globale
│                    │   • Findings détaillés
│                    │   • Plan d'action
│                    │   • Conclusion
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 4. Vérification    │ ← AGENT VÉRIFICATEUR
│    Qualité         │   • Cohérence
│                    │   • Complétude
│                    │   • Qualité rédactionnelle
└─────────┬──────────┘
          │
          ├─── Corrections nécessaires ? ───┐
          │                                  │
          ▼ OUI                              │ NON
┌────────────────────┐                      │
│ 5. Corrections     │                      │
│    Agent Créateur  │                      │
└─────────┬──────────┘                      │
          │                                  │
          └────────────────────────────┬────┘
                                       │
                                       ▼
                          ┌────────────────────┐
                          │ 6. Assemblage      │
                          │    Final du Rapport│
                          └─────────┬──────────┘
                                    │
                                    ▼
                          ┌────────────────────┐
                          │ 7. Génération      │
                          │    Format Final    │
                          │    (PDF/DOCX/HTML) │
                          └─────────┬──────────┘
                                    │
                                    ▼
                                 [FIN]
```

### 4.2 Détail des Étapes

#### Étape 1 : Extraction Base de Données
- Récupération des données d'audit via `queries.py`
- Chargement des findings avec leur sévérité
- Récupération des métadonnées contextuelles
- Construction d'un objet `AuditData` typé

#### Étape 2 : Initialisation State
```python
class ReportState(TypedDict):
    audit_data: AuditData
    sections: Dict[str, Section]
    validation_results: List[ValidationResult]
    corrections: List[Correction]
    final_report: Optional[Report]
    iteration: int
```

#### Étape 3 : Génération par l'Agent Créateur
Pour chaque section :
1. **Prompt contextualisé** avec données spécifiques
2. **Enrichissement IA** des descriptions techniques
3. **Génération de contenu** adapté au secteur du client
4. **Stockage dans le state** pour traçabilité

Sections générées :
- **Page de garde** : Identité client, type d'audit, date
- **Résumé exécutif** : Synthèse pour la direction (1 page)
- **Contexte & Périmètre** : Environnement audité
- **Méthodologie** : Standards utilisés (ISO27001, OWASP, etc.)
- **Analyse globale** : Niveau de sécurité, matrice des risques
- **Findings détaillés** : Chaque vulnérabilité enrichie
- **Plan d'action** : Mesures priorisées avec timeline
- **Conclusion** : Récapitulatif et perspectives

#### Étape 4 : Vérification par l'Agent Vérificateur
Critères de validation :
- **Cohérence** : Les sections se complètent sans contradiction
- **Complétude** : Toutes les informations obligatoires présentes
- **Qualité technique** : Précision des termes, pertinence des recommandations
- **Clarté** : Compréhensible pour un non-technique
- **Actionabilité** : Les recommandations sont concrètes

#### Étape 5 : Boucle de Correction
- Si validation échouée : retour à l'Agent Créateur avec feedback
- Maximum 3 itérations pour éviter les boucles infinies
- Traçabilité des corrections appliquées

#### Étape 6 : Assemblage
- Fusion de toutes les sections validées
- Application du template de mise en forme
- Vérification finale de la structure

#### Étape 7 : Génération Format Final
- **PDF** : Pour impression et archivage (ReportLab)
- **DOCX** : Pour édition post-génération (python-docx)
- **HTML** : Pour visualisation web (Jinja2)

---

## 5. Structure du Rapport Final

### Détail des 8 Sections

#### 1. Page de Garde
```yaml
Contenu:
  - Logo Nexoryx (optionnel)
  - Titre: "Rapport d'Audit de Sécurité"
  - Nom du client
  - Type d'audit (Pentest, ISO27001, SOC2, etc.)
  - Date de l'audit
  - Nom de l'auditeur
  - Version du rapport
```

#### 2. Résumé Exécutif (Généré par IA)
```yaml
Contenu:
  - Vision synthétique (3-5 paragraphes)
  - Niveau de risque global (Critical/High/Medium/Low)
  - Nombre de vulnérabilités par sévérité
  - 3-5 recommandations prioritaires
  - Timeline suggérée de remédiation
Cible: Direction, COMEX
Longueur: 1 page maximum
```

#### 3. Contexte & Périmètre
```yaml
Source: Table 'audits', champ 'scope'
Contenu:
  - Environnement audité (réseau, applications, cloud...)
  - Périmètre technique (IP, domaines, APIs...)
  - Périmètre temporel (dates, durée)
  - Contraintes et limitations
  - Contacts et interlocuteurs
```

#### 4. Méthodologie
```yaml
Généré automatiquement selon le type d'audit:
  - Pentest: OWASP, PTES, OSSTMM
  - ISO27001: Référentiel ISO, clauses auditées
  - SOC2: Critères TSC (Trust Services Criteria)
  - Cloud: CIS Benchmarks, Well-Architected Framework
Contenu:
  - Standards et frameworks utilisés
  - Outils et techniques
  - Phases de l'audit
  - Approche méthodologique
```

#### 5. Analyse Globale (Généré par IA)
```yaml
Contenu:
  a) Évaluation du niveau de sécurité
     - Score global (ex: 65/100)
     - Positionnement par rapport aux standards
     - Comparaison sectorielle

  b) Matrice des Risques
     ┌──────────────────────────────────────┐
     │      IMPACT                          │
     │   Low  Medium  High  Critical        │
     ├──────────────────────────────────────┤
     │ C │  1  │   3   │  2   │   5        │ Critical
     │ H │  4  │   8   │  6   │   1        │ High
     │ M │  7  │   5   │  2   │   0        │ Medium
     │ L │  3  │   1   │  0   │   0        │ Low
     └──────────────────────────────────────┘
       LIKELIHOOD

  c) Distribution par Sévérité
     - Critical: X findings
     - High: X findings
     - Medium: X findings
     - Low: X findings

  d) Distribution par Catégorie
     - Network Security: X%
     - Application Security: X%
     - IAM: X%
     - Cloud Security: X%
     - Governance: X%
```

#### 6. Findings Détaillés (Enrichis par IA)
```yaml
Pour chaque vulnérabilité:
  1. Titre
     Exemple: "Injection SQL sur le portail client"

  2. Catégorie
     Exemples: Network, AppSec, IAM, Cloud, Governance

  3. Description Enrichie (IA)
     - Description technique détaillée
     - Conditions d'exploitation
     - Contexte applicatif
     - Vecteurs d'attaque

  4. Impact Métier (IA)
     - Conséquences business
     - Risques financiers
     - Risques réputationnels
     - Risques légaux (RGPD, etc.)

  5. Risque Associé
     - Likelihood: Critical/High/Medium/Low
     - Impact: Critical/High/Medium/Low
     - Risque = Likelihood × Impact

  6. Preuve
     - Captures d'écran
     - Extraits de logs
     - Code vulnérable
     - Requêtes malveillantes

  7. Recommandation Enrichie (IA)
     - Mesures de correction détaillées
     - Étapes d'implémentation
     - Ressources nécessaires
     - Alternatives possibles
     - Meilleures pratiques

  8. Priorité d'Action
     - P0: Immédiat (< 1 semaine)
     - P1: Court terme (< 1 mois)
     - P2: Moyen terme (1-3 mois)
     - P3: Long terme (> 3 mois)
```

#### 7. Plan d'Action Priorisé (Généré par IA)
```yaml
Tableau structuré:
  ┌─────────────────┬──────────┬─────────────┬──────────┬──────────────────┐
  │ Mesure          │ Priorité │ Responsable │ Deadline │ Bénéfice         │
  ├─────────────────┼──────────┼─────────────┼──────────┼──────────────────┤
  │ Correction SQL  │   P0     │ Dev Lead    │ 1 sem.   │ Empêche exfil.   │
  │ Patch firewall  │   P0     │ NetOps      │ 2 sem.   │ Bloque accès ext.│
  │ Activation MFA  │   P1     │ IT Admin    │ 1 mois   │ Réduit compromis │
  │ Formation sécu  │   P2     │ HR/RSSI     │ 3 mois   │ Awareness accrue │
  │ Audit IAM       │   P2     │ RSSI        │ 3 mois   │ Cleanup comptes  │
  └─────────────────┴──────────┴─────────────┴──────────┴──────────────────┘

Contenu IA:
  - Priorisation intelligente basée sur risque × impact
  - Suggestions de responsables selon la catégorie
  - Deadlines réalistes selon complexité
  - Bénéfices métier explicités
  - Dépendances entre mesures
  - Estimation budgétaire (optionnel)
```

#### 8. Conclusion (Généré par IA)
```yaml
Contenu:
  - Récapitulatif du niveau de sécurité
  - Progrès réalisés (si audit récurrent)
  - Points positifs identifiés
  - Axes d'amélioration majeurs
  - Recommandations stratégiques
  - Perspectives et suivi
  - Remerciements
Longueur: 1/2 page
```

---

## 6. Différenciation et Valeur Ajoutée

### 6.1 Par rapport aux solutions manuelles

| Critère | Solution Manuelle | Solution IA Nexoryx | Gain |
|---------|-------------------|---------------------|------|
| **Temps de génération** | 3-5 jours | 15-30 minutes | 97% |
| **Cohérence** | Variable | Toujours élevée | Qualité garantie |
| **Enrichissement** | Dépend de l'auditeur | Systématique | Standardisé |
| **Personnalisation** | Limitée | Contextualisée | Pertinence accrue |
| **Erreurs** | Possibles | Minimisées | Fiabilité |

### 6.2 Avantages Concurrentiels

1. **Rapidité** : Génération en moins de 30 minutes vs plusieurs jours
2. **Qualité** : Double validation automatique (créateur + vérificateur)
3. **Richesse** : Enrichissement IA des descriptions et recommandations
4. **Personnalisation** : Contextualisation selon le secteur du client
5. **Cohérence** : Structure et qualité garanties
6. **Traçabilité** : Historique des modifications et décisions
7. **Scalabilité** : Génération simultanée de multiples rapports
8. **Multi-format** : PDF, DOCX, HTML selon les besoins

### 6.3 ROI Estimé

**Hypothèses** :
- 100 audits/an
- Temps moyen manuel : 4 jours/rapport
- Coût journalier auditeur : 500€
- Temps automatisé : 30 min supervision + génération

**Gains annuels** :
- Temps économisé : 400 jours × 500€ = 200 000€
- Réduction erreurs : ~30 000€ (reprises, insatisfaction)
- Capacité accrue : +50% d'audits sans embauche
- **ROI total estimé : 230 000€/an**

---

## 7. Roadmap d'Implémentation

### Phase 1 : Fondations (Semaines 1-2)
- [x] Création des modèles de données typés (Pydantic)
- [x] Mise en place de LangGraph et workflow de base
- [x] Implémentation Agent Créateur v1
- [x] Implémentation Agent Vérificateur v1
- [x] Tests unitaires des composants

### Phase 2 : Enrichissement (Semaines 3-4)
- [ ] Amélioration des prompts agents
- [ ] Ajout de la contextualisation sectorielle
- [ ] Génération de la matrice des risques
- [ ] Implémentation du plan d'action priorisé
- [ ] Boucle de correction automatique

### Phase 3 : Génération Rapports (Semaines 5-6)
- [ ] Templating Jinja2
- [ ] Génération PDF (ReportLab)
- [ ] Génération DOCX (python-docx)
- [ ] Génération HTML responsive
- [ ] Gestion des images et graphiques

### Phase 4 : Interface & Tests (Semaines 7-8)
- [ ] Interface Streamlit
- [ ] Tests d'intégration complets
- [ ] Tests de charge (génération multiple)
- [ ] Documentation utilisateur
- [ ] Formation équipe Nexoryx

### Phase 5 : Production (Semaine 9+)
- [ ] Déploiement en production
- [ ] Monitoring et logging
- [ ] Collecte de feedback utilisateurs
- [ ] Itérations d'amélioration

---

## 8. Métriques de Succès

### Indicateurs de Performance (KPIs)

1. **Temps de génération** : < 30 minutes par rapport
2. **Taux de satisfaction client** : > 85% (vs <60% actuel)
3. **Taux d'erreur** : < 5%
4. **Nombre de corrections manuelles** : < 10% du contenu
5. **Temps de validation** : < 15 minutes
6. **Réutilisation sans modification** : > 80% du contenu généré

### Critères de Qualité

- **Cohérence** : 95% des sections passent la validation du premier coup
- **Complétude** : 100% des champs obligatoires renseignés
- **Pertinence** : 90% des recommandations jugées actionnables
- **Lisibilité** : Score Flesch-Kincaid > 50

---

## 9. Sécurité et Conformité

### Gestion des Données Sensibles

1. **Données d'audit** : Stockées localement (SQLite), pas de cloud
2. **Prompts LLM** : Anonymisation des noms de clients dans les appels API
3. **Rapports générés** : Chiffrement optionnel (AES-256)
4. **Logs** : Pas de stockage d'informations sensibles

### Conformité RGPD

- Données personnelles minimales
- Droit à l'effacement implémenté
- Consentement explicite pour stockage
- Traçabilité des traitements

---

## 10. Coûts et Licensing

### Coûts d'Infrastructure

| Composant | Coût Estimé | Fréquence |
|-----------|-------------|-----------|
| API OpenAI (GPT-4) | 0.01€/page | Par utilisation |
| Serveur (si déployé) | 50€/mois | Mensuel |
| Stockage | Négligeable | Inclus |
| **Total par rapport** | **~2€** | Par génération |
| **Total annuel (100 rapports)** | **~200€** | Annuel |

### Licenses Logicielles

Toutes les bibliothèques utilisées sont open-source (MIT/Apache) :
- Python : PSF License
- LangGraph : MIT
- Pydantic : MIT
- ReportLab : BSD-like
- python-docx : MIT
- Streamlit : Apache 2.0

---

## 11. Conclusion

Cette solution combine les dernières avancées en IA générative et en orchestration multi-agents pour résoudre durablement les problèmes de qualité des rapports d'audit de Nexoryx.

### Points Clés

- **Architecture robuste** : Multi-agents avec validation automatique
- **Technologie éprouvée** : Stack Python + LangGraph + LLMs de pointe
- **ROI significatif** : 230k€/an estimés
- **Scalabilité** : Passage à l'échelle sans surcoût
- **Qualité garantie** : Double vérification systématique

### Prochaines Étapes

1. Validation de l'offre technique par Nexoryx
2. Lancement du développement du prototype
3. Tests avec 3-5 audits réels
4. Ajustements basés sur les retours
5. Déploiement progressif en production
