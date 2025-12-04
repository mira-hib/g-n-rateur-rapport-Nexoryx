from typing import Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint
from config.settings import settings


class LLMFactory:
    """Factory pour créer des instances de LLM selon le provider configuré."""

    @staticmethod
    def create_llm(temperature: float = None) -> Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, HuggingFaceEndpoint]:
        """
        Crée une instance de LLM selon le provider et la configuration.

        Args:
            temperature: Température optionnelle (utilise settings.temperature si None)

        Returns:
            Instance du LLM configuré

        Raises:
            ValueError: Si la configuration est invalide ou le provider non supporté
        """
        is_valid, error_msg = settings.validate_configuration()
        if not is_valid:
            raise ValueError(f"Configuration invalide: {error_msg}")

        provider = settings.ai_provider
        model_name = settings.get_model_name()
        temp = temperature if temperature is not None else settings.temperature

        if provider == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                api_key=settings.openai_api_key
            )
        elif provider == "claude":
            return ChatAnthropic(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                api_key=settings.anthropic_api_key
            )
        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temp,
                max_output_tokens=settings.max_tokens,
                google_api_key=settings.gemini_api_key
            )
        elif provider == "zephyr":
            return HuggingFaceEndpoint(
                repo_id=model_name,
                temperature=temp,
                max_new_tokens=settings.max_tokens,
                huggingfacehub_api_token=settings.huggingface_api_key
            )
        else:
            raise ValueError(f"Provider non supporté: {provider}")