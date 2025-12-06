# 📂 Structure du Projet - Générateur de Rapports Nexoryx

```
générateur-rapport/
│
├── 📝 README.md                    # Documentation centrale et point d'entrée
├── 🚀 setup.bat                    # Script d'installation Windows
├── 🚀 setup.sh                     # Script d'installation Linux/Mac
├── ⚙️ .env.example                 # Template de configuration
├── 📋 requirements.txt             # Dépendances Python
├── 🚫 .gitignore                   # Fichiers à ignorer par git
│
├── 🤖 agents/                      # Agents IA (1,354 lignes - modulaire)
│   ├── __init__.py                 # Exports principaux
│   ├── prompts/                    # Prompts LLM (378 lignes)
│   │   ├── __init__.py
│   │   ├── generation_prompts.py  # 4 prompts de génération
│   │   └── validation_prompts.py  # 5 prompts de validation
│   ├── creator/                    # Agent Créateur (326 lignes)
│   │   ├── __init__.py             # CreatorAgent
│   │   ├── llm_factory.py          # Factory multi-provider (4 IA)
│   │   ├── content_generator.py    # Génération de contenu
│   │   └── parser_utils.py         # Parsing réponses LLM
│   ├── validator/                  # Agent Validateur (244 lignes)
│   │   ├── __init__.py             # ValidatorAgent
│   │   ├── content_validator.py    # Validation qualité (scoring)
│   │   └── parser_utils.py         # Parsing validation
│   └── workflow/                   # Workflow LangGraph (351 lignes)
│       ├── __init__.py             # ReportGenerationWorkflow
│       ├── builder.py              # Construction du graphe
│       └── nodes.py                # 13 nœuds de traitement
│
├── 📊 models/                      # Modèles Pydantic v2 (460 lignes)
│   ├── __init__.py
│   ├── audit_models.py             # AuditData, AuditFinding, Enums
│   ├── report_models.py            # 8 sections + FullReport
│   └── state_models.py             # ReportState, ValidationResult
│
├── 🗄️ db/                          # Base de données
│   ├── database.py                 # Connexion SQLite
│   ├── init_db.py                  # Initialisation + seed data (6 audits)
│   ├── audit_service.py            # Service d'accès orienté objet
│   └── audit_system.db             # DB SQLite (créée par init_db.py)
│
├── 📄 report/                      # Générateurs de rapports
│   ├── __init__.py
│   ├── pdf_generator.py            # Génération PDF (ReportLab)
│   └── docx_generator.py           # Génération DOCX (python-docx)
│
├── ⚙️ config/                      # Configuration
│   ├── __init__.py
│   └── settings.py                 # Settings multi-provider Pydantic
│
├── 📚 docs/                        # Documentation détaillée (145+ pages)
│   ├── README.md                   # Index de la documentation
│   ├── QUICK_START.md              # Guide complet (~30 pages)
│   ├── OFFRE_TECHNIQUE.md          # Architecture détaillée (~60 pages)
│   ├── LIVRABLE_FINAL.md           # Récapitulatif livrable (~20 pages)
│   ├── GUIDE_INTERFACE.md          # Guide interface Streamlit (~10 pages)
│   └── MULTI_PROVIDERS_GUIDE.md    # Config 4 providers IA (~15 pages)
│
├── 📁 generated_reports/           # Rapports générés (créé auto)
│   ├── *.pdf                       # Rapports PDF
│   └── *.docx                      # Rapports DOCX
│
├── 🖥️ main.py                      # Interface CLI (185 lignes)
├── 🌐 app.py                       # Interface Streamlit (246 lignes)
└── ▶️ run_app.bat                  # Script lancement Streamlit Windows

```

## 📊 Statistiques du Code

| Composant | Fichiers | Lignes | Description |
|-----------|----------|--------|-------------|
| **agents/** | 14 | 1,354 | Agents IA modulaires |
| **models/** | 4 | 460 | Modèles Pydantic v2 |
| **report/** | 3 | 450 | Générateurs PDF/DOCX |
| **db/** | 3 | 450 | Base de données |
| **config/** | 2 | 120 | Configuration |
| **main.py** | 1 | 185 | Interface CLI |
| **app.py** | 1 | 246 | Interface Streamlit |
| **docs/** | 6 | 145+ pages | Documentation |
| **TOTAL** | 34 | ~3,265 | Code production-ready |

**Tous les fichiers ≤ 265 lignes** pour une maintenabilité optimale.

## 🔑 Fichiers Clés

### Points d'Entrée
- **setup.bat / setup.sh** - Installation automatique (recommandé)
- **main.py** - Interface CLI pour automatisation
- **app.py** - Interface web Streamlit pour utilisateurs

### Configuration
- **.env.example** - Template de configuration multi-provider
- **config/settings.py** - Validation configuration Pydantic
- **requirements.txt** - Dépendances Python (20 packages)

### Documentation
- **README.md** - Documentation centrale condensée (point d'entrée)
- **docs/QUICK_START.md** - Guide complet d'installation et utilisation
- **docs/OFFRE_TECHNIQUE.md** - Architecture et workflow détaillés

### Code Principal
- **agents/workflow/** - Orchestration LangGraph (13 nœuds)
- **agents/creator/** - Génération contenu IA
- **agents/validator/** - Validation qualité IA
- **models/** - Modèles de données typés
- **report/** - Génération PDF/DOCX

## 🎯 Navigation Rapide

**Pour installer :**
```bash
# Windows
setup.bat

# Linux/Mac
./setup.sh
```

**Pour utiliser :**
```bash
# CLI
python main.py --list-audits
python main.py --audit-id 1 --format pdf

# Web
streamlit run app.py
```

**Pour comprendre :**
- Lire `README.md`
- Lire `docs/QUICK_START.md`
- Explorer `agents/workflow/`

## 🏗️ Architecture Modulaire

Le projet suit les principes **SOLID** et **Clean Code** :
- ✅ **Single Responsibility** : 1 module = 1 fonction
- ✅ **Fichiers ≤ 265 lignes** : Maintenabilité maximale
- ✅ **Docstrings complets** : Classes et méthodes documentées
- ✅ **Type hints Pydantic** : Validation runtime stricte
- ✅ **Tests inclus** : test_pdf_generation.py
- ✅ **Factory Pattern** : LLMFactory partagée

## 📦 Dépendances Principales

| Package | Version | Usage |
|---------|---------|-------|
| langchain | 0.3+ | Framework LLM |
| langgraph | 0.2+ | Orchestration multi-agents |
| pydantic | 2.x | Validation et typage |
| streamlit | 1.x | Interface web |
| reportlab | 4.x | Génération PDF |
| python-docx | 1.x | Génération DOCX |
| openai | 1.x | Provider OpenAI |
| anthropic | 0.40+ | Provider Claude |
| google-generativeai | 0.8+ | Provider Gemini |

Voir `requirements.txt` pour la liste complète (20 packages).

---

**Version** : 1.0.0 | **Date** : 2024-12-06 | **Statut** : ✅ Production-Ready
