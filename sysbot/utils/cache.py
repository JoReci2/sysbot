"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Dict, Optional, Union, List
from cryptography.fernet import Fernet
import base64
import os
import json


class Cache:

    def __init__(self, no_current_error: str = "No current connection."):
        self.secrets = SecretsManager()
        self.connections = ConnectionsManager(no_current_error)

    def empty_cache(self) -> None:
        self.connections.clear_all()
        self.secrets.clear_all()

    def get_cache_stats(self) -> Dict[str, Any]:
        return {
            "connections": self.connections.get_stats(),
            "secrets": self.secrets.get_stats(),
        }

    def __len__(self) -> int:
        return len(self.connections) + len(self.secrets)


class ConnectionsManager:
    """Gestionnaire pour les connexions avec support d'alias et index."""

    def __init__(self, no_current_error: str = "No current connection."):
        self._connections: Dict[int, Any] = {}
        self._aliases: Dict[str, int] = {}
        self._current_index: Optional[int] = None
        self._no_current_error = no_current_error

    def register(self, connection: Any, alias: Optional[str] = None) -> int:
        """Enregistre une connexion avec un alias optionnel.

        Args:
            connection: L'objet connexion à enregistrer
            alias: Alias optionnel pour la connexion

        Returns:
            L'index de la connexion enregistrée
        """
        index = self._get_next_index()
        self._connections[index] = connection
        self._current_index = index

        if alias:
            self._aliases[alias] = index

        return index

    def get(self, index_or_alias: Union[int, str, None] = None) -> Any:
        """Récupère une connexion par index ou alias.

        Args:
            index_or_alias: Index (int), alias (str) ou None pour la connexion courante

        Returns:
            L'objet connexion

        Raises:
            RuntimeError: Si la connexion n'existe pas ou aucune connexion courante
        """
        if index_or_alias is None:
            if self._current_index is None:
                raise RuntimeError(self._no_current_error)
            return self._connections[self._current_index]

        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        return self._connections[index]

    def switch(self, index_or_alias: Union[int, str]) -> Any:
        """Change la connexion courante et la retourne.

        Args:
            index_or_alias: Index (int) ou alias (str) de la connexion

        Returns:
            L'objet connexion
        """
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        self._current_index = index
        return self._connections[index]

    def close_all(self, closer_method: str = "close") -> None:
        """Ferme toutes les connexions.

        Args:
            closer_method: Nom de la méthode à appeler pour fermer les connexions
        """
        for connection in self._connections.values():
            if hasattr(connection, closer_method):
                try:
                    getattr(connection, closer_method)()
                except Exception:
                    # Ignore les erreurs lors de la fermeture
                    pass

        self.clear_all()

    def close(
        self, index_or_alias: Union[int, str, None] = None, closer_method: str = "close"
    ) -> None:
        """Ferme une connexion spécifique.

        Args:
            index_or_alias: Index, alias ou None pour la connexion courante
            closer_method: Nom de la méthode à appeler pour fermer la connexion
        """
        if index_or_alias is None:
            if self._current_index is None:
                raise RuntimeError(self._no_current_error)
            index = self._current_index
        else:
            index = self._resolve_index(index_or_alias)

        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        connection = self._connections[index]
        if hasattr(connection, closer_method):
            try:
                getattr(connection, closer_method)()
            except Exception:
                # Ignore les erreurs lors de la fermeture
                pass

        # Supprime la connexion et les alias associés
        del self._connections[index]
        self._aliases = {
            alias: idx for alias, idx in self._aliases.items() if idx != index
        }

        # Reset la connexion courante si c'était celle-ci
        if self._current_index == index:
            self._current_index = None

    def clear_all(self) -> None:
        """Vide le cache sans fermer les connexions."""
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

    def remove(self, index_or_alias: Union[int, str]) -> None:
        """Supprime une connexion sans la fermer.

        Args:
            index_or_alias: Index ou alias de la connexion à supprimer
        """
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        del self._connections[index]
        self._aliases = {
            alias: idx for alias, idx in self._aliases.items() if idx != index
        }

        if self._current_index == index:
            self._current_index = None

    @property
    def current(self) -> Any:
        """Retourne la connexion courante.

        Returns:
            L'objet connexion courante

        Raises:
            RuntimeError: Si aucune connexion courante
        """
        if self._current_index is None:
            raise RuntimeError(self._no_current_error)
        return self._connections[self._current_index]

    @property
    def current_index(self) -> Optional[int]:
        """Retourne l'index de la connexion courante."""
        return self._current_index

    def has_connection(self, index_or_alias: Union[int, str]) -> bool:
        """Vérifie si une connexion existe.

        Args:
            index_or_alias: Index ou alias de la connexion

        Returns:
            True si la connexion existe, False sinon
        """
        try:
            index = self._resolve_index(index_or_alias)
            return index in self._connections
        except ValueError:
            return False

    def list_connections(self) -> List[Dict[str, Any]]:
        """Retourne la liste des connexions avec leurs informations.

        Returns:
            Liste des connexions avec index, alias et type
        """
        result = []
        reverse_aliases = {idx: alias for alias, idx in self._aliases.items()}

        for index, connection in self._connections.items():
            result.append(
                {
                    "index": index,
                    "alias": reverse_aliases.get(index),
                    "type": type(connection).__name__,
                    "is_current": index == self._current_index,
                }
            )

        return result

    def get_all_connections(self) -> Dict[int, Any]:
        """Retourne toutes les connexions."""
        return self._connections.copy()

    def get_all_aliases(self) -> Dict[str, int]:
        """Retourne tous les alias."""
        return self._aliases.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les connexions."""
        return {
            "total": len(self._connections),
            "current_index": self._current_index,
            "aliases_count": len(self._aliases),
        }

    def _get_next_index(self) -> int:
        """Génère le prochain index disponible."""
        if not self._connections:
            return 1
        return max(self._connections.keys()) + 1

    def _resolve_index(self, index_or_alias: Union[int, str]) -> int:
        """Résout un alias en index ou retourne l'index directement.

        Args:
            index_or_alias: Index (int) ou alias (str)

        Returns:
            L'index de la connexion

        Raises:
            ValueError: Si l'alias n'existe pas
        """
        if isinstance(index_or_alias, int):
            return index_or_alias

        if isinstance(index_or_alias, str):
            if index_or_alias in self._aliases:
                return self._aliases[index_or_alias]
            # Tenter de convertir en int si c'est un string numérique
            try:
                return int(index_or_alias)
            except ValueError:
                raise ValueError(f"Alias '{index_or_alias}' does not exist.")

        raise ValueError(f"Invalid index or alias type: {type(index_or_alias)}")

    def __len__(self) -> int:
        """Retourne le nombre de connexions."""
        return len(self._connections)

    def __contains__(self, index_or_alias: Union[int, str]) -> bool:
        """Vérifie si une connexion existe (support de l'opérateur 'in')."""
        return self.has_connection(index_or_alias)


class SecretsManager:
    """Gestionnaire sécurisé pour les secrets avec chiffrement Fernet."""

    def __init__(self):
        self._secrets: Dict[str, bytes] = {}  # Stockage des secrets chiffrés
        self._fernet_key = self._get_or_generate_key()
        self._cipher = Fernet(self._fernet_key)

    def _get_or_generate_key(self) -> bytes:
        """Génère ou récupère une clé de chiffrement Fernet."""
        # Essaie d'abord de récupérer la clé depuis une variable d'environnement
        key_env = os.getenv("SYSBOT_ENCRYPTION_KEY")
        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env.encode())
            except Exception:
                pass

        # Génère une nouvelle clé si aucune n'est trouvée
        key = Fernet.generate_key()

        # Optionnel : stocker la clé dans les variables d'environnement pour la session
        os.environ["SYSBOT_ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key).decode()

        return key

    def store_secret(self, secret_name: str, secret_value: str) -> None:
        """Stocke un secret de manière chiffrée.

        Args:
            secret_name: Nom/identifiant du secret
            secret_value: Valeur du secret à chiffrer

        Raises:
            ValueError: Si la valeur n'est pas une string
        """
        if not isinstance(secret_value, str):
            raise ValueError("Secret value must be a string")

        encrypted_secret = self._cipher.encrypt(secret_value.encode())
        self._secrets[secret_name] = encrypted_secret

    def get_secret(self, secret_name: str) -> str:
        """Récupère un secret déchiffré.

        Args:
            secret_name: Nom/identifiant du secret

        Returns:
            La valeur déchiffrée du secret

        Raises:
            KeyError: Si le secret n'existe pas
            Exception: Si le déchiffrement échoue
        """
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        try:
            encrypted_secret = self._secrets[secret_name]
            decrypted_value = self._cipher.decrypt(encrypted_secret)
            return decrypted_value.decode()
        except Exception as e:
            raise Exception(f"Failed to decrypt secret '{secret_name}': {str(e)}")

    def store_secret_dict(self, secret_name: str, secret_dict: Dict[str, Any]) -> None:
        """Stocke un dictionnaire de secrets sous un nom.

        Args:
            secret_name: Nom/identifiant du groupe de secrets
            secret_dict: Dictionnaire contenant les secrets

        Raises:
            ValueError: Si le dictionnaire n'est pas valide
        """
        if not isinstance(secret_dict, dict):
            raise ValueError("Secret dict must be a dictionary")

        # Convertir toutes les valeurs en strings pour la sérialisation
        serializable_dict = {}
        for key, value in secret_dict.items():
            if isinstance(value, (str, int, float, bool)):
                serializable_dict[key] = str(value)
            elif isinstance(value, dict):
                # Support pour dictionnaires imbriqués
                serializable_dict[key] = value
            else:
                raise ValueError(
                    f"Unsupported value type for key '{key}': {type(value)}"
                )

        json_string = json.dumps(serializable_dict, indent=None, separators=(",", ":"))
        self.store_secret(secret_name, json_string)

    def get_secret_dict(self, secret_name: str) -> Dict[str, Any]:
        """Récupère un dictionnaire de secrets.

        Args:
            secret_name: Nom/identifiant du groupe de secrets

        Returns:
            Dictionnaire contenant les secrets déchiffrés

        Raises:
            Exception: Si la désérialisation échoue
        """
        json_string = self.get_secret(secret_name)
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse secret dict '{secret_name}': {str(e)}")

    def get_secret_value(self, secret_reference: str) -> str:
        """Récupère une valeur de secret avec support de la notation pointée.

        Args:
            secret_reference: Référence au secret (ex: "db_config.password" ou "api_key")

        Returns:
            La valeur du secret

        Raises:
            KeyError: Si le secret ou le champ n'existe pas
        """
        if "." in secret_reference:
            # Notation pointée pour accéder à un champ spécifique d'un dictionnaire
            secret_name, field_path = secret_reference.split(".", 1)
            secret_dict = self.get_secret_dict(secret_name)

            # Support de la notation pointée multiple (ex: "config.database.password")
            current_value = secret_dict
            for field in field_path.split("."):
                if isinstance(current_value, dict) and field in current_value:
                    current_value = current_value[field]
                else:
                    raise KeyError(
                        f"Field '{field}' not found in secret '{secret_name}'"
                    )

            return str(current_value)
        else:
            # Secret simple
            return self.get_secret(secret_reference)

    def has_secret(self, secret_name: str) -> bool:
        """Vérifie si un secret existe.

        Args:
            secret_name: Nom/identifiant du secret

        Returns:
            True si le secret existe, False sinon
        """
        return secret_name in self._secrets

    def remove_secret(self, secret_name: str) -> None:
        """Supprime un secret.

        Args:
            secret_name: Nom/identifiant du secret

        Raises:
            KeyError: Si le secret n'existe pas
        """
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        del self._secrets[secret_name]

    def list_secrets(self) -> List[str]:
        """Retourne la liste des noms de secrets stockés.

        Returns:
            Liste des noms de secrets
        """
        return list(self._secrets.keys())

    def clear_all(self) -> None:
        """Supprime tous les secrets du cache."""
        self._secrets.clear()

    def update_secret(self, secret_name: str, secret_value: str) -> None:
        """Met à jour un secret existant ou en crée un nouveau.

        Args:
            secret_name: Nom/identifiant du secret
            secret_value: Nouvelle valeur du secret
        """
        self.store_secret(secret_name, secret_value)

    def update_secret_dict_field(
        self, secret_name: str, field_path: str, new_value: str
    ) -> None:
        """Met à jour un champ spécifique dans un dictionnaire de secrets.

        Args:
            secret_name: Nom du dictionnaire de secrets
            field_path: Chemin vers le champ (ex: "database.password")
            new_value: Nouvelle valeur
        """
        secret_dict = self.get_secret_dict(secret_name)

        # Naviguer jusqu'au champ parent
        fields = field_path.split(".")
        current_dict = secret_dict

        for field in fields[:-1]:
            if field not in current_dict or not isinstance(current_dict[field], dict):
                current_dict[field] = {}
            current_dict = current_dict[field]

        # Mettre à jour le champ final
        current_dict[fields[-1]] = new_value

        # Sauvegarder le dictionnaire modifié
        self.store_secret_dict(secret_name, secret_dict)

    def export_key(self) -> str:
        """Exporte la clé de chiffrement (pour backup/partage sécurisé).

        Returns:
            La clé de chiffrement encodée en base64
        """
        return base64.urlsafe_b64encode(self._fernet_key).decode()

    def import_key(self, key_b64: str) -> None:
        """Importe une clé de chiffrement.

        Args:
            key_b64: Clé encodée en base64

        Raises:
            ValueError: Si la clé n'est pas valide
        """
        try:
            key = base64.urlsafe_b64decode(key_b64.encode())
            # Tester la clé
            test_cipher = Fernet(key)
            # Si ça marche, utiliser la nouvelle clé
            self._fernet_key = key
            self._cipher = test_cipher
            os.environ["SYSBOT_ENCRYPTION_KEY"] = key_b64
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {str(e)}")

    def get_stats(self) -> Dict[str, int]:
        """Retourne des statistiques sur les secrets stockés.

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            "total_secrets": len(self._secrets),
            "total_size_bytes": sum(len(secret) for secret in self._secrets.values()),
        }

    def __len__(self) -> int:
        """Retourne le nombre de secrets stockés."""
        return len(self._secrets)

    def __contains__(self, secret_name: str) -> bool:
        """Vérifie si un secret existe (support de l'opérateur 'in')."""
        return secret_name in self._secrets
