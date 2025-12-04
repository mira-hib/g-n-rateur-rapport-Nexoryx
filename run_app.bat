@echo off
echo ========================================
echo   Nexoryx - Generateur de Rapports
echo ========================================
echo.

REM Activer l'environnement virtuel si disponible
if exist .venv\Scripts\activate.bat (
    echo Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
)

echo Lancement de l'interface Streamlit...
echo.
echo L'interface s'ouvrira dans votre navigateur.
echo Pour arreter l'application, appuyez sur Ctrl+C
echo.

streamlit run app.py

pause
