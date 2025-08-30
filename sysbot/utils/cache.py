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

    def __init__(self, no_current_error: str = "No current connection."):
        self._connections: Dict[int, Any] = {}
        self._aliases: Dict[str, int] = {}
        self._current_index: Optional[int] = None
        self._no_current_error = no_current_error

    def register(self, connection: Any, alias: Optional[str] = None) -> int:
        index = self._get_next_index()
        self._connections[index] = connection
        self._current_index = index
        
        if alias:
            self._aliases[alias] = index
            
        return index

    def get_connection(self, index_or_alias: Union[int, str, None] = None) -> Any:
        if index_or_alias is None:
            if self._current_index is None:
                raise RuntimeError(self._no_current_error)
            return self._connections[self._current_index]
        
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")
        
        return self._connections[index]

    def switch(self, index_or_alias: Union[int, str]) -> Any:
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")
        
        self._current_index = index
        return self._connections[index]

    def close_all(self, closer_method: str = "close") -> None:
        for connection in self._connections.values():
            if hasattr(connection, closer_method):
                try:
                    getattr(connection, closer_method)()
                except Exception:
                    pass
        
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

    def close(self, index_or_alias: Union[int, str, None] = None, 
              closer_method: str = "close") -> None:
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
                pass
        
        del self._connections[index]
        self._aliases = {alias: idx for alias, idx in self._aliases.items() if idx != index}
        
        if self._current_index == index:
            self._current_index = None

    def empty_cache(self) -> None:
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

    @property
    def current(self) -> Any:
        if self._current_index is None:
            raise RuntimeError(self._no_current_error)
        return self._connections[self._current_index]

    @property
    def current_index(self) -> Optional[int]:
        return self._current_index

    def _get_next_index(self) -> int:
        if not self._connections:
            return 1
        return max(self._connections.keys()) + 1

    def _resolve_index(self, index_or_alias: Union[int, str]) -> int:
        if isinstance(index_or_alias, int):
            return index_or_alias
        
        if isinstance(index_or_alias, str):
            if index_or_alias in self._aliases:
                return self._aliases[index_or_alias]
            try:
                return int(index_or_alias)
            except ValueError:
                raise ValueError(f"Alias '{index_or_alias}' does not exist.")
        
        raise ValueError(f"Invalid index or alias type: {type(index_or_alias)}")

    def __len__(self) -> int:
        return len(self._connections)

    def __contains__(self, index_or_alias: Union[int, str]) -> bool:
        try:
            index = self._resolve_index(index_or_alias)
            return index in self._connections
        except ValueError:
            return False

    def get_all_connections(self) -> Dict[int, Any]:
        return self._connections.copy()

    def get_all_aliases(self) -> Dict[str, int]:
        return self._aliases.copy()