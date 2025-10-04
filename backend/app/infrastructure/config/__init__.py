"""
Configuration Services.

Infrastructure Layer - Clean Architecture

Services pour charger les configurations depuis fichiers YAML.

Pourquoi dans Infrastructure?
- Le chargement de fichiers est un détail d'implémentation
- Le Domain/Application ne doivent pas savoir qu'on utilise YAML
- On pourrait changer pour JSON, env vars, base de données, etc.

Services:
- YAMLConfigurationLoader: Charge configs depuis fichiers YAML
"""

from app.infrastructure.config.yaml_config_loader import YAMLConfigurationLoader

__all__ = ["YAMLConfigurationLoader"]
