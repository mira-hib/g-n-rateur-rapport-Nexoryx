# Guide de Démarrage Rapide

## Étapes d'installation et de test

### 1. Installer les dépendances

**Note**: sqlite3 est déjà inclus dans Python, retirons-le de requirements.txt

```bash
cd "d:\test nexora\générateur de rapport"

# Créer et activer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate

# Installer les dépendances
pip install langgraph langchain langchain-openai langchain-anthropic openai anthropic langchain_google_genai langchain_huggingface
pip install pydantic pydantic-settings
pip install reportlab python-docx Jinja2 Pillow
pip install streamlit python-dotenv typing-extensions

```

### 2. Configurer les clés API

Créer un fichier `.env` :

```env
OPENAI_API_KEY=sk-votre-clé-ici
# ou
# ANTHROPIC_API_KEY=sk-ant-votre-clé-ici

DEFAULT_MODEL=gpt-4o
TEMPERATURE=0.3
MAX_ITERATIONS=3
```

### 3. Initialiser la base de données

```bash
python db/init_db.py
```

### 4. Lister les audits disponibles

```bash
python main.py --list-audits
```

### 5. Générer un rapport de test

```bash
# Générer un rapport PDF pour l'audit #1
python main.py --audit-id 1 --format pdf

# Le rapport sera dans: generated_reports/
```

## Prochaines étapes

- Voir [README.md](README.md) pour la documentation complète
- Voir [OFFRE_TECHNIQUE.md](OFFRE_TECHNIQUE.md) pour l'architecture détaillée

## Note importante

**IMPORTANT**: Ce prototype nécessite une clé API OpenAI ou Anthropic active pour fonctionner. Sans clé API, la génération de rapport échouera.

Pour tester sans API (mode démo), vous devrez :
1. Modifier `config/settings.py` pour désactiver l'enrichissement IA
2. Ou utiliser des modèles locaux (non implémenté dans le MVP)

## Support

En cas de problème, vérifiez :
- Python 3.11+ installé
- Toutes les dépendances installées
- Clé API configurée dans `.env`
- Base de données initialisée
