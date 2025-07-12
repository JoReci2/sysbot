# Configuration GitHub Copilot pour SysBot

## Description du projet

SysBot est un outil d'automatisation et de gestion de systèmes qui fournit une interface unifiée pour se connecter et gérer divers systèmes via différents protocoles. 

### Fonctionnalités principales :
- **Support multi-protocoles** : SSH, HTTP, WinRM et plus
- **Tunneling SSH** : Support pour les tunnels SSH imbriqués
- **Opérations sur fichiers** : Exécution de scripts et récupération de résultats à distance
- **Multi-plateforme** : Support pour Linux et Windows
- **Intégration Robot Framework** : Support intégré pour l'automatisation Robot Framework
- **Sécurité de type** : Support complet des annotations de type et analyse statique

## Structure du repository

```
sysbot/
├── .github/                 # Configuration GitHub et Copilot
├── .gitlab-ci.yml          # Configuration CI/CD GitLab
├── docs/                   # Documentation du projet
├── sysbot/                 # Code source principal
│   ├── __init__.py
│   ├── Helper.py           # Fonctions utilitaires principales
│   ├── connectors/         # Connecteurs spécifiques aux protocoles
│   │   ├── ConnectorHandler.py  # Classe gestionnaire principale
│   │   ├── ssh/            # Implémentations du protocole SSH
│   │   │   ├── linux.py    # Connecteur SSH Linux
│   │   │   ├── windows.py  # Connecteur SSH Windows
│   │   │   └── utils/      # Utilitaires SSH
│   │   ├── http/           # Implémentations du protocole HTTP
│   │   └── winrm/          # Implémentations du protocole WinRM
│   ├── dataloaders/        # Utilitaires de chargement de données
│   └── utils/              # Utilitaires généraux
├── tests/                  # Tests unitaires
│   ├── test_Helper.py
│   ├── test_connector_handler.py
│   ├── test_dataloader_handler.py
│   └── test_listener_http.py
├── README.md               # Documentation principale
├── setup.py                # Configuration d'installation
├── pyproject.toml          # Configuration de build
└── LICENSE                 # Licence MIT
```

## Bonnes pratiques de développement

### Tests unitaires
- **Maintenir les tests à jour** : Chaque nouvelle fonctionnalité doit être accompagnée de tests correspondants
- **Couverture de code** : Viser une couverture de test élevée pour le code critique
- **Tests avant commit** : Exécuter tous les tests avant chaque commit avec `pytest tests/`
- **Isolation des tests** : Chaque test doit être indépendant et reproductible

### Qualité du code
- **Formatage** : Utiliser `black sysbot/` pour le formatage automatique
- **Vérification de types** : Utiliser `mypy sysbot/` pour la vérification statique des types
- **Linting** : Utiliser `flake8 sysbot/` pour l'analyse de code
- **Documentation** : Maintenir la documentation à jour dans le README.md et les docstrings

### Gestion des branches
- **Nommage des branches** : Les noms de branches doivent avoir un rapport direct avec l'issue associée
  - Format recommandé : `feature/issue-<numéro>-<description-courte>`
  - Exemple : `feature/issue-11-add-copilot-config`
  - Pour les corrections : `fix/issue-<numéro>-<description-courte>`
  - Pour les améliorations : `enhancement/issue-<numéro>-<description-courte>`

### Workflow de développement
1. **Avant chaque commit** :
   - Exécuter les tests : `pytest tests/`
   - Vérifier le formatage : `black --check sysbot/`
   - Vérifier les types : `mypy sysbot/`
   - Vérifier le linting : `flake8 sysbot/`

2. **Documentation** :
   - Mettre à jour le README.md pour les nouvelles fonctionnalités
   - Ajouter ou mettre à jour les docstrings pour les nouvelles méthodes/classes
   - Maintenir la documentation dans le dossier `docs/` si applicable

3. **Pull Requests** :
   - Inclure une description claire des changements
   - Référencer l'issue associée
   - S'assurer que tous les tests passent
   - Demander une revue de code avant le merge

### Dépendances
- **Installation de développement** : `pip install -e ".[dev]"`
- **Dépendances principales** : robotframework, paramiko, sshtunnel, netmiko, redfish, pyVmomi, pywinrm, pyOpenSSL
- **Python** : Minimum version 3.7+

### Conventions de code
- Suivre les conventions PEP 8
- Utiliser des annotations de type pour toutes les fonctions publiques
- Privilégier la lisibilité et la maintenabilité
- Éviter les dépendances externes non nécessaires
- Documenter les fonctions complexes avec des exemples d'utilisation