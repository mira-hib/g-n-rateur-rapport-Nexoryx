#!/bin/bash

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  Générateur de Rapports d'Audit Nexoryx - Installation Linux/Mac ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Fonction pour afficher les messages
print_step() {
    echo -e "${BLUE}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC}  $1"
}

# [1/6] Vérifier Python
print_step "1/6" "Vérification de Python..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 n'est pas installé"
    echo ""
    echo "Veuillez installer Python 3.11+ :"
    echo "  - Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "  - macOS: brew install python@3.11"
    echo "  - Fedora: sudo dnf install python3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION détecté"

# Vérifier si la version est >= 3.11
python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Python 3.11 ou supérieur est requis"
    echo "Votre version: $PYTHON_VERSION"
    exit 1
fi

# [2/6] Créer l'environnement virtuel
echo ""
print_step "2/6" "Création de l'environnement virtuel..."

if [ -d ".venv" ]; then
    print_info "Environnement virtuel existant détecté"
    read -p "Voulez-vous le recréer? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Suppression de l'ancien environnement..."
        rm -rf .venv
        python3 -m venv .venv
        if [ $? -ne 0 ]; then
            print_error "Erreur lors de la création de l'environnement virtuel"
            exit 1
        fi
        print_success "Environnement virtuel créé"
    fi
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        print_error "Erreur lors de la création de l'environnement virtuel"
        exit 1
    fi
    print_success "Environnement virtuel créé"
fi

# [3/6] Activer l'environnement virtuel
echo ""
print_step "3/6" "Activation de l'environnement virtuel..."

source .venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Erreur lors de l'activation de l'environnement virtuel"
    exit 1
fi
print_success "Environnement virtuel activé"

# [4/6] Mettre à jour pip
echo ""
print_step "4/6" "Mise à jour de pip..."

python -m pip install --upgrade pip --quiet
print_success "pip mis à jour"

# [5/6] Installer les dépendances
echo ""
print_step "5/6" "Installation des dépendances..."
print_info "Cela peut prendre plusieurs minutes..."

pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    print_error "Erreur lors de l'installation des dépendances"
    echo "Essayez d'exécuter manuellement: pip install -r requirements.txt"
    exit 1
fi
print_success "Dépendances installées"

# [6/6] Configuration initiale
echo ""
print_step "6/6" "Configuration initiale..."

# Créer le fichier .env si inexistant
if [ ! -f ".env" ]; then
    echo "Création du fichier .env..."
    cp .env.example .env
    print_success "Fichier .env créé depuis .env.example"
    print_warning "IMPORTANT: Éditez .env et ajoutez votre clé API"
else
    print_info "Fichier .env existant détecté"
fi

# Créer le dossier generated_reports si inexistant
if [ ! -d "generated_reports" ]; then
    mkdir -p generated_reports
    print_success "Dossier generated_reports créé"
fi

# Initialiser la base de données
if [ ! -f "db/audit_system.db" ]; then
    echo "Initialisation de la base de données..."
    python db/init_db.py
    if [ $? -ne 0 ]; then
        print_error "Erreur lors de l'initialisation de la base de données"
        exit 1
    fi
    print_success "Base de données initialisée avec 6 audits d'exemple"
else
    print_info "Base de données existante détectée"
    read -p "Voulez-vous la réinitialiser? (les données seront perdues) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm db/audit_system.db
        python db/init_db.py
        print_success "Base de données réinitialisée"
    fi
fi

# Message de succès final
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    Installation terminée ! ✅                     ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Éditez le fichier .env et ajoutez votre clé API:"
echo "   - OpenAI: OPENAI_API_KEY=sk-..."
echo "   - Claude: ANTHROPIC_API_KEY=sk-ant-..."
echo "   - Gemini: GEMINI_API_KEY=..."
echo "   - Zephyr: HUGGINGFACE_API_KEY=hf_..."
echo ""
echo "2. Activez l'environnement virtuel:"
echo "   source .venv/bin/activate"
echo ""
echo "3. Utilisez le système:"
echo "   - Interface CLI:  python main.py --list-audits"
echo "   - Interface Web:  streamlit run app.py"
echo ""
echo "4. Pour plus d'informations:"
echo "   - Voir README.md"
echo "   - Voir docs/QUICK_START.md"
echo ""
