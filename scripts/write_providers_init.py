"""Write app/providers/__init__.py with proper content."""

import os

content = '''"""Provider registry and factory."""

from app.config.settings import settings
from app.providers.llm import DeepSeekProvider, LLMProvider

_PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "deepseek": DeepSeekProvider,
}


def get_llm_provider(name: str | None = None) -> LLMProvider:
    """Create and return an LLM provider instance by name.

    Args:
        name: Provider name (e.g., 'deepseek'). Defaults to
              settings.LLM_PROVIDER.

    Returns:
        An instance of the requested LLM provider.

    Raises:
        ValueError: If the provider name is not registered.
    """
    provider_name = (name or settings.LLM_PROVIDER).lower()
    provider_cls = _PROVIDER_MAP.get(provider_name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown LLM provider: {provider_name!r}. "
            f"Available: {list(_PROVIDER_MAP.keys())}"
        )
    return provider_cls()


__all__ = [
    "LLMProvider",
    "get_llm_provider",
]
'''

target = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app",
    "providers",
    "__init__.py",
)

with open(target, "w") as f:
    f.write(content)

print(f"Written to {target}")
