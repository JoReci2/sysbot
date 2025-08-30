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

from typing import Any, Dict, Optional, Union


class Cache:
    """Cache pour gérer les connexions avec alias et index.
    
    Inspiré de robot.utils.ConnectionCache pour réduire les dépendances.
    """

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

    def get_connection(self, index_or_alias: Union[int, str, None] = None) -> Any:
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
        
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

    def close(self, index_or_alias: Union[int, str, None] = None, 
              closer_method: str = "close") -> None:
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
        self._aliases = {alias: idx for alias, idx in self._aliases.items() if idx != index}
        
        # Reset la connexion courante si c'était celle-ci
        if self._current_index == index:
            self._current_index = None

    def empty_cache(self) -> None:
        """Vide le cache sans fermer les connexions."""
        self._connections.clear()
        self._aliases.clear()
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
        """Retourne le nombre de connexions dans le cache."""
        return len(self._connections)

    def __contains__(self, index_or_alias: Union[int, str]) -> bool:
        """Vérifie si une connexion existe dans le cache."""
        try:
            index = self._resolve_index(index_or_alias)
            return index in self._connections
        except ValueError:
            return False

    def get_all_connections(self) -> Dict[int, Any]:
        """Retourne toutes les connexions."""
        return self._connections.copy()

    def get_all_aliases(self) -> Dict[str, int]:
        """Retourne tous les alias."""
        return self._aliases.copy()