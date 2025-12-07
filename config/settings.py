"""
Configuration de l'application avec support multi-providers IA.

Providers supportés:
- OpenAI (GPT-4, GPT-4 Turbo, etc.)
- Google Gemini (Gemini Pro, Gemini Flash)
- Claude (Claude 3.5 Sonnet, Claude 3 Opus, etc.)
- Zephyr (via HuggingFace)
"""

import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


# Type pour les providers IA supportés
AIProvider = Literal["openai", "gemini", "claude", "zephyr"]


class Settings(BaseSettings):
    """Configuration de l'application avec gestion des variables d'environnement."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==========================================
    # CONFIGURATION DU PROVIDER IA
    # ==========================================

    ai_provider: AIProvider = ""
    """Provider IA à utiliser: 'openai', 'gemini', 'claude', ou 'zephyr'"""
    
    api_key_dict : dict[str, Optional[str]] = {
    }
    
    @staticmethod
    def registry_api_keys(api_key_dict : dict[str, Optional[str]], name : str, key: Optional[str]) -> None:
        """Enregistre les clés API dans un dictionnaire pour accès facile."""
        api_key_dict[name] = key

    # Clés API pour chaque provider
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None  # Google API Key
    anthropic_api_key: Optional[str] = None  # Claude
    huggingface_api_key: Optional[str] = None  # Pour Zephyr
    

    # ==========================================
    # CONFIGURATION DES MODÈLES PAR PROVIDER
    # ==========================================

    # OpenAI
    openai_model: Optional[str] = None
    """Modèle OpenAI: gpt-4o, gpt-4-turbo, gpt-3.5-turbo, etc."""

    # Google Gemini
    gemini_model: Optional[str] = None
    """Modèle Gemini: gemini-1.5-pro, gemini-1.5-flash, gemini-pro, etc."""

    # Anthropic Claude
    claude_model: Optional[str] = None
    """Modèle Claude: claude-3-5-sonnet-20241022, claude-3-opus-20240229, etc."""

    # Zephyr (HuggingFace)
    zephyr_model: Optional[str] = None
    """Modèle Zephyr via HuggingFace"""

    # ==========================================
    # PARAMÈTRES DE GÉNÉRATION
    # ==========================================

    temperature: float = 0.3
    """Température de génération (0.0 = déterministe, 1.0 = créatif)"""

    max_tokens: int = 16000
    """Nombre maximum de tokens par réponse"""

    # ==========================================
    # CONFIGURATION LANGGRAPH
    # ==========================================

    max_iterations: int = 3
    """Nombre maximum d'itérations de correction"""

    checkpoint_enabled: bool = True
    """Activer la sauvegarde de l'état du workflow"""

    # ==========================================
    # CONFIGURATION DE GÉNÉRATION
    # ==========================================

    enable_enrichment: bool = True
    """Activer l'enrichissement IA des sections"""

    enable_validation: bool = True
    """Activer la validation automatique"""

    min_validation_score: float = 75.0
    """Score minimum de validation (0-100)"""

    # ==========================================
    # CHEMINS
    # ==========================================

    database_path: str = "audit_system.db"
    """Chemin vers la base de données SQLite"""

    reports_output_dir: str = "generated_reports"
    """Répertoire de sortie des rapports générés"""

    templates_dir: str = "templates"
    """Répertoire des templates"""

    assets_dir: str = "assets"
    """Répertoire des assets (logos, images)"""

    # ==========================================
    # LOGS
    # ==========================================

    log_level: str = "INFO"
    """Niveau de log: DEBUG, INFO, WARNING, ERROR"""

    log_file: str = "app.log"
    """Fichier de log"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.reports_output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        self.registry_api_keys(self.api_key_dict, "openai", self.openai_api_key)
        self.registry_api_keys(self.api_key_dict,"gemini", self.gemini_api_key)
        self.registry_api_keys(self.api_key_dict,"claude", self.anthropic_api_key)
        self.registry_api_keys(self.api_key_dict,"zephyr", self.huggingface_api_key)



    def get_api_key(self) -> Optional[str]:
        """
        Retourne la clé API du provider configuré.

        Returns:
            Clé API ou None si non configurée
        """
        if self.api_key_dict.get(self.ai_provider) is not None:
            return self.api_key_dict[self.ai_provider]
        return None

    def get_model_name(self) -> str:
        """
        Retourne le nom du modèle selon le provider configuré.

        Returns:
            Nom du modèle
        """
        if self.ai_provider == "openai":
            return self.openai_model
        elif self.ai_provider == "gemini":
            return self.gemini_model
        elif self.ai_provider == "claude":
            return self.claude_model
        elif self.ai_provider == "zephyr":
            return self.zephyr_model
        return self.openai_model  # Défaut

    def validate_configuration(self) -> tuple[bool, str]:
        """
        Valide que la configuration du provider est correcte.

        Returns:
            (is_valid, error_message)
        """
        api_key = self.get_api_key()

        if not api_key:
            return False, f"Clé API manquante pour le provider '{self.ai_provider}'"

        if self.ai_provider not in ["openai", "gemini", "claude", "zephyr"]:
            return False, f"Provider '{self.ai_provider}' non supporté"

        return True, ""


# Instance globale
settings = Settings()
print(settings.gemini_api_key)
