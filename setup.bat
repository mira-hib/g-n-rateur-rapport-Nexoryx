@echo off
chcp 65001 >nul
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║  Générateur de Rapports d'Audit Nexoryx - Installation Windows  ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM Vérifier si Python est installé
echo [1/6] Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.11+ depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher "Add Python to PATH" pendant l'installation
    pause
    exit /b 1
)

REM Vérifier la version de Python
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% détecté

REM Vérifier si la version est >= 3.11
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11 ou supérieur est requis
    echo Votre version: %PYTHON_VERSION%
    pause
    exit /b 1
)

echo.
echo [2/6] Création de l'environnement virtuel...
if exist .venv (
    echo ℹ️  Environnement virtuel existant détecté
    choice /C YN /M "Voulez-vous le recréer"
    if errorlevel 2 goto skip_venv
    echo Suppression de l'ancien environnement...
    rmdir /s /q .venv
)

python -m venv .venv
if errorlevel 1 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel créé

:skip_venv
echo.
echo [3/6] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erreur lors de l'activation de l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ Environnement virtuel activé

echo.
echo [4/6] Mise à jour de pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip mis à jour

echo.
echo [5/6] Installation des dépendances...
echo ℹ️  Cela peut prendre plusieurs minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    echo Essayez d'exécuter manuellement: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dépendances installées

echo.
echo [6/6] Configuration initiale...

REM Créer le fichier .env si inexistant
if not exist .env (
    echo Création du fichier .env...
    copy .env.example .env >nul
    echo ✅ Fichier .env créé depuis .env.example
    echo ⚠️  IMPORTANT: Éditez .env et ajoutez votre clé API
) else (
    echo ℹ️  Fichier .env existant détecté
)

REM Créer le dossier generated_reports si inexistant
if not exist generated_reports (
    mkdir generated_reports
    echo ✅ Dossier generated_reports créé
)

REM Initialiser la base de données
if not exist db\audit_system.db (
    echo Initialisation de la base de données...
    python db\init_db.py
    if errorlevel 1 (
        echo ❌ Erreur lors de l'initialisation de la base de données
        pause
        exit /b 1
    )
    echo ✅ Base de données initialisée avec 6 audits d'exemple
) else (
    echo ℹ️  Base de données existante détectée
    choice /C YN /M "Voulez-vous la réinitialiser (les données seront perdues)"
    if not errorlevel 2 (
        del db\audit_system.db
        python db\init_db.py
        echo ✅ Base de données réinitialisée
    )
)

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║                    Installation terminée ! ✅                     ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo Prochaines étapes:
echo.
echo 1. Éditez le fichier .env et ajoutez votre clé API:
echo    - OpenAI: OPENAI_API_KEY=sk-...
echo    - Claude: ANTHROPIC_API_KEY=sk-ant-...
echo    - Gemini: GEMINI_API_KEY=...
echo    - Zephyr: HUGGINGFACE_API_KEY=hf_...
echo.
echo 2. Activez l'environnement virtuel:
echo    .venv\Scripts\activate
echo.
echo 3. Utilisez le système:
echo    - Interface CLI:  python main.py --list-audits
echo    - Interface Web:  streamlit run app.py
echo    - Ou:             run_app.bat
echo.
echo 4. Pour plus d'informations:
echo    - Voir README.md
echo    - Voir docs\QUICK_START.md
echo.
pause
