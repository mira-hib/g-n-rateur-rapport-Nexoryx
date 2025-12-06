# 🚀 Guide de Démarrage Rapide - Générateur de Rapports Nexoryx

Ce guide couvre tout ce dont vous avez besoin pour installer, configurer et utiliser le générateur de rapports d'audit.

---

## 📋 Table des Matières

1. [Installation](#installation)
2. [Configuration Multi-Provider](#configuration-multi-provider)
3. [Utilisation CLI](#utilisation-cli)
4. [Utilisation Interface Web](#utilisation-interface-web)
5. [Dépannage](#dépannage)

---

## Installation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Clé API d'un provider IA (OpenAI, Claude, Gemini, ou HuggingFace)

### Étape 1 : Cloner/Télécharger le Projet

```bash
cd "d:\test nexora\générateur de rapport"
```

### Étape 2 : Créer l'Environnement Virtuel

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Étape 3 : Installer les Dépendances

```bash
pip install -r requirements.txt
```

**Ou installation manuelle** :

```bash
# Framework IA
pip install langgraph langchain langchain-openai langchain-anthropic
pip install langchain_google_genai langchain_huggingface

# Validation et typage
pip install pydantic pydantic-settings

# Génération de rapports
pip install reportlab python-docx Jinja2 Pillow

# Interface et utilitaires
pip install streamlit python-dotenv typing-extensions
```

### Étape 4 : Initialiser la Base de Données

```bash
python db/init_db.py
```

Cette commande crée `db/audit_system.db` avec des données d'exemple.

---

## Configuration Multi-Provider

Le système supporte **4 providers IA** : OpenAI, Google Gemini, Anthropic Claude, et Zephyr (HuggingFace).

### Providers Disponibles

| Provider | Modèles | Qualité | Coût | Open-Source |
|----------|---------|---------|------|-------------|
| **OpenAI** | GPT-4o, GPT-4-turbo, GPT-3.5 | ⭐⭐⭐⭐⭐ | $$ | ❌ |
| **Gemini** | gemini-1.5-pro, gemini-1.5-flash | ⭐⭐⭐⭐⭐ | $ | ❌ |
| **Claude** | claude-3-5-sonnet, claude-3-opus | ⭐⭐⭐⭐⭐ | $$ | ❌ |
| **Zephyr** | zephyr-7b-beta | ⭐⭐⭐ | Gratuit | ✅ |

### Configuration Étape par Étape

#### 1. Créer le fichier `.env`

Copiez `.env.example` et renommez-le en `.env` :

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

#### 2. Choisir et Configurer un Provider

##### Option A : OpenAI (Recommandé pour Production)

```env
# Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Paramètres
TEMPERATURE=0.3
MAX_TOKENS=16000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=true
MAX_ITERATIONS=3
MIN_VALIDATION_SCORE=75.0
```

**Obtenir la clé** :
1. Créer un compte sur https://platform.openai.com/
2. Aller dans **API keys**
3. Créer une nouvelle clé (format : `sk-...`)

##### Option B : Google Gemini (Économique)

```env
# Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro

# Paramètres
TEMPERATURE=0.3
MAX_TOKENS=16000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=true
```

**Obtenir la clé** :
1. Aller sur https://makersuite.google.com/app/apikey
2. Créer une clé API
3. Copier la clé

##### Option C : Anthropic Claude (Qualité Maximale)

```env
# Provider
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Paramètres
TEMPERATURE=0.2
MAX_TOKENS=16000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=true
```

**Obtenir la clé** :
1. Créer un compte sur https://console.anthropic.com/
2. Aller dans **API keys**
3. Créer une nouvelle clé (format : `sk-ant-...`)

##### Option D : Zephyr/HuggingFace (Open-Source)

```env
# Provider
AI_PROVIDER=zephyr
HUGGINGFACE_API_KEY=hf_...
ZEPHYR_MODEL=HuggingFaceH4/zephyr-7b-beta

# Paramètres
TEMPERATURE=0.4
MAX_TOKENS=4000
ENABLE_ENRICHMENT=true
ENABLE_VALIDATION=false  # Optionnel pour Zephyr
```

**Obtenir la clé** :
1. Créer un compte sur https://huggingface.co/
2. Aller dans **Settings > Access Tokens**
3. Créer un token (format : `hf_...`)

### Paramètres Optionnels

```env
# Répertoire de sortie des rapports
REPORTS_OUTPUT_DIR=generated_reports

# Checkpointing LangGraph (sauvegarde état)
CHECKPOINT_ENABLED=false

# Logging
LOG_LEVEL=INFO
```

---

## Utilisation CLI

### Lister les Audits Disponibles

```bash
python main.py --list-audits
```

**Sortie** :
```
=== Audits disponibles ===

ID: 1
  Client: Nexoryx Bank
  Type: Pentest Réseau
  Date: 2024-01-15

ID: 2
  Client: CloudPlus SAS
  Type: Audit Cloud AWS
  Date: 2024-02-20

Total: 2 audit(s)
```

### Générer un Rapport PDF

```bash
python main.py --audit-id 1 --format pdf
```

### Générer un Rapport DOCX

```bash
python main.py --audit-id 1 --format docx
```

### Générer les Deux Formats

```bash
python main.py --audit-id 1 --format both
```

### Workflow Complet

```bash
# 1. Lister les audits
python main.py --list-audits

# 2. Générer le rapport
python main.py --audit-id 1 --format pdf

# 3. Le rapport sera dans : generated_reports/rapport_Nexoryx_Bank_20241204.pdf
```

**Temps de génération** : 15-30 minutes selon le nombre de findings

---

## Utilisation Interface Web

### Lancer l'Interface Streamlit

```bash
streamlit run app.py
```

**Ou sur Windows** :
```bash
run_app.bat
```

L'interface s'ouvre automatiquement à : **http://localhost:8501**

### Workflow en 3 Étapes

#### Étape 1 : Sélectionner un Audit

1. **Liste déroulante** affiche tous les audits de la DB
2. Format : `#ID - Client (Type) - Date`
3. Sélectionnez un audit
4. Message de confirmation : `✅ Audit chargé: [Client] - [X] vulnérabilités`

#### Étape 2 : Modifier les Informations (Optionnel)

Tous les champs sont pré-remplis et modifiables :

**Informations principales** :
- Nom du client
- Type d'audit
- Auditeur
- Date de l'audit
- Périmètre

**Statistiques automatiques** :
- 🔴 Vulnérabilités Critiques
- 🟠 Vulnérabilités Élevées
- 🟡 Vulnérabilités Moyennes
- 🟢 Vulnérabilités Faibles

**Détails des vulnérabilités** :
- Consultables dans l'expander
- Titre, catégorie, sévérité, description

#### Étape 3 : Générer le Rapport

**3 boutons de génération** :

1. **📄 Générer PDF** - Format professionnel pour présentation/archivage
2. **📝 Générer DOCX** - Format éditable pour modifications
3. **📚 Générer PDF + DOCX** - Les deux formats simultanément

**Après génération** :
- Boutons de téléchargement directs
- Les fichiers sont dans `generated_reports/`

### Fonctionnalités Avancées

#### Configuration dans l'Interface

Si besoin de changer de provider ou paramètres :
1. Éditer `.env`
2. Redémarrer Streamlit (`Ctrl+C` puis `streamlit run app.py`)

#### Test sans Attendre le LLM

```bash
# Tester la génération PDF/DOCX avec des données mockées
python test_pdf_generation.py
```

#### Charger depuis la Base de Données

L'interface charge automatiquement depuis `db/audit_system.db` via `AuditService`.

---

## Dépannage

### Erreur : "Configuration invalide"

**Cause** : Clé API manquante ou provider mal configuré

**Solution** :
1. Vérifier `.env` existe
2. Vérifier `AI_PROVIDER` est l'un de : `openai`, `gemini`, `claude`, `zephyr`
3. Vérifier la clé API correspondante est définie

**Exemple** :
```env
# ❌ Mauvais
AI_PROVIDER=gpt4

# ✅ Correct
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Erreur : "Audit introuvable"

**Cause** : Base de données non initialisée ou ID invalide

**Solution** :
```bash
# Réinitialiser la DB
python db/init_db.py

# Lister les IDs valides
python main.py --list-audits
```

### Erreur : "Module not found"

**Cause** : Dépendances manquantes

**Solution** :
```bash
pip install -r requirements.txt
```

### L'interface Streamlit ne se lance pas

**Cause** : Streamlit non installé ou port occupé

**Solution** :
```bash
# Réinstaller Streamlit
pip install --upgrade streamlit

# Changer le port
streamlit run app.py --server.port 8502
```

### Performance lente

**Causes possibles** :
- Modèle LLM lent (Zephyr, GPT-4)
- Validation activée (double appel LLM)
- Nombre de findings élevé

**Solutions** :
```env
# Modèle plus rapide
GEMINI_MODEL=gemini-1.5-flash
# ou
OPENAI_MODEL=gpt-3.5-turbo

# Désactiver validation
ENABLE_VALIDATION=false

# Réduire itérations
MAX_ITERATIONS=1
```

### PDF/DOCX ne s'affiche pas correctement

**Solutions** :
- Ouvrir avec Adobe Reader (PDF) ou Microsoft Word (DOCX)
- Vérifier les polices sont disponibles
- Télécharger à nouveau le fichier

### Erreur lors de la génération

**Vérifications** :
1. Tous les champs obligatoires remplis (nom client, au moins 1 finding)
2. Répertoire `generated_reports/` existe
3. Consulter les logs d'erreur affichés

**Activer logs détaillés** :
```env
LOG_LEVEL=DEBUG
```

---

## Conseils d'Utilisation

### Priorités d'Actions

- **P0 (Immédiat)** : < 1 semaine - Vulnérabilités critiques
- **P1 (Court terme)** : < 1 mois - Vulnérabilités importantes
- **P2 (Moyen terme)** : 1-3 mois - Améliorations significatives
- **P3 (Long terme)** : > 3 mois - Optimisations

### Sévérité des Vulnérabilités

- **CRITICAL** : Exploitation immédiate possible, impact majeur
- **HIGH** : Exploitation probable, impact significatif
- **MEDIUM** : Exploitation possible, impact modéré
- **LOW** : Exploitation difficile, impact mineur

### Catégories

- **Network** : Sécurité réseau et infrastructure
- **AppSec** : Sécurité applicative
- **IAM** : Gestion des identités et accès
- **Cloud** : Sécurité cloud
- **Governance** : Gouvernance et conformité
- **Forensic** : Investigation et analyse forensique

### Choisir le Bon Provider

**Production (qualité maximale)** :
- OpenAI GPT-4o ou Claude 3.5 Sonnet
- `ENABLE_VALIDATION=true`

**Tests/Développement (rapidité)** :
- Google Gemini Flash
- `ENABLE_VALIDATION=false`

**Confidentialité/On-Premise** :
- Zephyr (HuggingFace)
- Peut être hébergé localement

**Budget limité** :
- Gemini Flash (gratuit tier généreux)
- GPT-3.5-turbo (économique)

---

## Personnalisation

### Modifier les Couleurs

Éditer `app.py` section CSS :

```python
st.markdown("""
<style>
    .main-header {
        color: #VOTRE_COULEUR;  # Changer ici
    }
    .stButton>button {
        background-color: #VOTRE_COULEUR;  # Changer ici
    }
</style>
""", unsafe_allow_html=True)
```

### Ajouter un Logo

1. Créer le dossier `assets/`
2. Ajouter `logo.png`
3. Modifier `app.py` :

```python
st.image("assets/logo.png", width=200)
```

### Personnaliser les Styles PDF

Éditer `report/pdf_generator.py` :

```python
# Couleurs
self.primary_color = colors.HexColor('#VOTRE_COULEUR')

# Polices
self.styles['SectionTitle'].fontSize = 20  # Modifier taille
```

---

## Architecture Technique (Référence Rapide)

### Structure du Projet

```
générateur-rapport/
├── agents/                    # Agents IA modulaires
│   ├── prompts/              # Prompts LLM
│   ├── creator/              # Agent Créateur
│   ├── validator/            # Agent Validateur
│   └── workflow/             # Workflow LangGraph
├── db/                        # Base de données
│   ├── audit_system.db       # SQLite DB
│   ├── audit_service.py      # Service d'accès
│   └── init_db.py            # Initialisation
├── models/                    # Modèles Pydantic
├── report/                    # Générateurs PDF/DOCX
├── config/                    # Configuration
├── main.py                    # CLI
├── app.py                     # Interface Streamlit
└── .env                       # Configuration
```

### Workflow LangGraph

```
Chargement DB → Initialisation State →
Génération Sections (AI) → Validation (AI) →
Corrections (si nécessaire) → Assemblage →
Génération PDF/DOCX → Téléchargement
```

### 8 Sections du Rapport

1. **Page de Garde** : Client, type, date, auditeur
2. **Résumé Exécutif** (IA) : Synthèse pour direction
3. **Contexte & Périmètre** : Environnement audité
4. **Méthodologie** : Standards et frameworks
5. **Analyse Globale** : Score sécurité, matrices
6. **Findings Détaillés** (IA) : Vulnérabilités enrichies
7. **Plan d'Action** (IA) : Mesures priorisées
8. **Conclusion** (IA) : Récapitulatif et perspectives

---

## Support et Documentation

### Documentation Complète

- **README.md** : Vue d'ensemble et architecture
- **OFFRE_TECHNIQUE.md** : Architecture technique détaillée
- **LIVRABLE_FINAL.md** : Spécifications du livrable
- **.env.example** : Modèle de configuration

### Logs

Les logs sont affichés dans la console. Pour logs détaillés :

```env
LOG_LEVEL=DEBUG
```

### Tests

```bash
# Tester la génération sans LLM
python test_pdf_generation.py

# Tester les imports
python -c "from agents import ReportGenerationWorkflow; print('OK')"
```

### Contact

Pour toute question :
1. Consulter la documentation
2. Vérifier les logs d'erreur
3. Tester avec un provider différent
4. Contacter l'équipe technique Nexoryx

---

## Checklist de Démarrage

- [ ] Python 3.11+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé avec clé API
- [ ] Base de données initialisée (`python db/init_db.py`)
- [ ] Test CLI réussi (`python main.py --list-audits`)
- [ ] Interface Streamlit lancée (`streamlit run app.py`)
- [ ] Premier rapport généré avec succès

**Vous êtes prêt ! 🚀**

---

© 2024 Nexoryx - Générateur Automatisé de Rapports d'Audit
Version 1.0.0 - Dernière mise à jour : 2024-12-04
