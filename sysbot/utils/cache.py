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

    def get_all(self) -> Dict[int, Any]:
        """Retourne toutes les connexions."""
        return self._connections.copy()

    def clear(self, index_or_alias: Union[int, str]) -> None:
        """Supprime une connexion spécifique.

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

    def clear_all(self) -> None:
        """Vide toutes les connexions du cache."""
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

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

    def register(
        self, secret_name: str, secret_value: Union[str, Dict[str, Any], List[Any]]
    ) -> None:
        """Enregistre un secret (simple, dictionnaire ou liste).

        Args:
            secret_name: Nom/identifiant du secret
            secret_value: Valeur du secret (string, dictionnaire ou liste)

        Raises:
            ValueError: Si la valeur n'est pas supportée
        """
        if isinstance(secret_value, str):
            encrypted_secret = self._cipher.encrypt(secret_value.encode())
            self._secrets[secret_name] = encrypted_secret
        elif isinstance(secret_value, (dict, list)):
            # Convertir le dictionnaire ou la liste en JSON puis chiffrer
            json_string = json.dumps(secret_value, indent=None, separators=(",", ":"))
            encrypted_secret = self._cipher.encrypt(json_string.encode())
            self._secrets[secret_name] = encrypted_secret
        else:
            raise ValueError("Secret value must be a string, dictionary, or list")

    def switch(self, secret_name: str) -> Union[str, Dict[str, Any], List[Any]]:
        """Change le secret 'courant' et le retourne.

        Note: Pour les secrets, cette méthode équivaut à get()
        car il n'y a pas vraiment de notion de "secret courant"

        Args:
            secret_name: Nom du secret

        Returns:
            La valeur déchiffrée du secret
        """
        return self.get(secret_name)

    def get(self, secret_reference: str) -> Union[str, Dict[str, Any], List[Any]]:
        """Récupère un secret déchiffré avec support de la notation pointée.

        Args:
            secret_reference: Référence au secret (ex: "db_config.password" ou "api_key")

        Returns:
            La valeur déchiffrée du secret

        Raises:
            KeyError: Si le secret n'existe pas
            Exception: Si le déchiffrement échoue
        """
        if "." in secret_reference:
            # Notation pointée pour accéder à un champ spécifique d'un dictionnaire ou liste
            secret_name, field_path = secret_reference.split(".", 1)
            secret_value = self._get_secret(secret_name)

            # Support de la notation pointée multiple (ex: "config.database.password")
            current_value = secret_value
            for field in field_path.split("."):
                if isinstance(current_value, dict) and field in current_value:
                    current_value = current_value[field]
                elif isinstance(current_value, list):
                    try:
                        # Support de l'accès par index pour les listes
                        index = int(field)
                        current_value = current_value[index]
                    except (ValueError, IndexError):
                        raise KeyError(
                            f"Field '{field}' not found in secret '{secret_name}'"
                        )
                else:
                    raise KeyError(
                        f"Field '{field}' not found in secret '{secret_name}'"
                    )

            return current_value
        else:
            # Secret simple
            return self._get_secret(secret_reference)

    def get_all(self) -> Dict[str, Union[str, Dict[str, Any], List[Any]]]:
        """Retourne tous les secrets déchiffrés.

        Returns:
            Dictionnaire avec tous les secrets déchiffrés
        """
        all_secrets = {}
        for secret_name in self._secrets.keys():
            try:
                all_secrets[secret_name] = self._get_secret(secret_name)
            except Exception:
                # Ignorer les secrets qui ne peuvent pas être déchiffrés
                continue
        return all_secrets

    def clear(self, secret_name: str) -> None:
        """Supprime un secret spécifique.

        Args:
            secret_name: Nom du secret à supprimer

        Raises:
            KeyError: Si le secret n'existe pas
        """
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        del self._secrets[secret_name]

    def clear_all(self) -> None:
        """Supprime tous les secrets du cache."""
        self._secrets.clear()

    def _get_secret(self, secret_name: str) -> Union[str, Dict[str, Any], List[Any]]:
        """Méthode privée pour récupérer et déchiffrer un secret."""
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        try:
            encrypted_secret = self._secrets[secret_name]
            decrypted_value = self._cipher.decrypt(encrypted_secret).decode()

            # Tenter de parser comme JSON pour les dictionnaires et listes
            try:
                return json.loads(decrypted_value)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, retourner comme string
                return decrypted_value

        except Exception as e:
            raise Exception(f"Failed to decrypt secret '{secret_name}': {str(e)}")

    def _get_secret_dict(self, secret_name: str) -> Dict[str, Any]:
        """Méthode privée pour récupérer un dictionnaire de secrets."""
        secret_value = self._get_secret(secret_name)
        if not isinstance(secret_value, dict):
            raise ValueError(f"Secret '{secret_name}' is not a dictionary")
        return secret_value

    def get_stats(self) -> Dict[str, int]:
        """Retourne des statistiques sur les secrets stockés."""
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
