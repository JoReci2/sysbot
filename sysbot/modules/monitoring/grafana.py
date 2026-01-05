"""
Grafana Module

This module provides methods for interacting with Grafana monitoring system via REST API.
It supports common operations such as health checks, datasource management, dashboard queries,
and user/organization management.

Note: This module uses the HTTP connector with API Key or Basic authentication.
Sessions should be opened with protocol="http" and product="apikey" or "basicauth".
"""

import json
from sysbot.utils.engine import ComponentBase


class Grafana(ComponentBase):
    """
    Grafana module for monitoring system management.
    
    This class provides methods to interact with Grafana systems using REST API
    via the HTTP connector with API Key or Basic authentication.
    All methods require an alias to identify the established HTTP session.
    """

    def health_check(self, alias: str, **kwargs) -> dict:
        """
        Check Grafana health status.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            dict: Health status information.
        """
        response = self.execute_command(alias, "/api/health", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_datasources(self, alias: str, **kwargs) -> list:
        """
        Get all configured datasources in Grafana.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            list: List of datasource configurations.
        """
        response = self.execute_command(alias, "/api/datasources", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_datasource_by_id(self, alias: str, datasource_id: int, **kwargs) -> dict:
        """
        Get a specific datasource by ID.

        Args:
            alias (str): The session alias for the Grafana connection.
            datasource_id (int): Datasource identifier.

        Returns:
            dict: Datasource configuration.
        """
        response = self.execute_command(
            alias,
            f"/api/datasources/{datasource_id}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_datasource_by_name(self, alias: str, datasource_name: str, **kwargs) -> dict:
        """
        Get a specific datasource by name.

        Args:
            alias (str): The session alias for the Grafana connection.
            datasource_name (str): Datasource name.

        Returns:
            dict: Datasource configuration.
        """
        response = self.execute_command(
            alias,
            f"/api/datasources/name/{datasource_name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def create_datasource(self, alias: str, config: dict, **kwargs) -> dict:
        """
        Create a new datasource.

        Args:
            alias (str): The session alias for the Grafana connection.
            config (dict): Datasource configuration containing name, type, url, etc.

        Returns:
            dict: Response from the creation operation.
        """
        response = self.execute_command(
            alias,
            "/api/datasources",
            options={"method": "POST", "json": config},
            **kwargs
        )
        return json.loads(response.decode())

    def update_datasource(self, alias: str, datasource_id: int, config: dict, **kwargs) -> dict:
        """
        Update an existing datasource.

        Args:
            alias (str): The session alias for the Grafana connection.
            datasource_id (int): Datasource identifier.
            config (dict): Updated datasource configuration.

        Returns:
            dict: Response from the update operation.
        """
        response = self.execute_command(
            alias,
            f"/api/datasources/{datasource_id}",
            options={"method": "PUT", "json": config},
            **kwargs
        )
        return json.loads(response.decode())

    def delete_datasource(self, alias: str, datasource_id: int, **kwargs) -> dict:
        """
        Delete a datasource by ID.

        Args:
            alias (str): The session alias for the Grafana connection.
            datasource_id (int): Datasource identifier.

        Returns:
            dict: Response from the deletion operation.
        """
        response = self.execute_command(
            alias,
            f"/api/datasources/{datasource_id}",
            options={"method": "DELETE"},
            **kwargs
        )
        return json.loads(response.decode())

    def search_dashboards(self, alias: str, query: str = "", **kwargs) -> list:
        """
        Search for dashboards.

        Args:
            alias (str): The session alias for the Grafana connection.
            query (str): Search query string (optional).

        Returns:
            list: List of dashboard search results.
        """
        endpoint = "/api/search"
        if query:
            endpoint += f"?query={query}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_dashboard_by_uid(self, alias: str, dashboard_uid: str, **kwargs) -> dict:
        """
        Get a dashboard by UID.

        Args:
            alias (str): The session alias for the Grafana connection.
            dashboard_uid (str): Dashboard unique identifier.

        Returns:
            dict: Dashboard configuration and metadata.
        """
        response = self.execute_command(
            alias,
            f"/api/dashboards/uid/{dashboard_uid}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_home_dashboard(self, alias: str, **kwargs) -> dict:
        """
        Get the home dashboard.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            dict: Home dashboard configuration.
        """
        response = self.execute_command(
            alias,
            "/api/dashboards/home",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def create_or_update_dashboard(self, alias: str, dashboard: dict, **kwargs) -> dict:
        """
        Create or update a dashboard.

        Args:
            alias (str): The session alias for the Grafana connection.
            dashboard (dict): Dashboard configuration containing dashboard JSON and metadata.

        Returns:
            dict: Response from the operation including dashboard ID and UID.
        """
        response = self.execute_command(
            alias,
            "/api/dashboards/db",
            options={"method": "POST", "json": dashboard},
            **kwargs
        )
        return json.loads(response.decode())

    def delete_dashboard_by_uid(self, alias: str, dashboard_uid: str, **kwargs) -> dict:
        """
        Delete a dashboard by UID.

        Args:
            alias (str): The session alias for the Grafana connection.
            dashboard_uid (str): Dashboard unique identifier.

        Returns:
            dict: Response from the deletion operation.
        """
        response = self.execute_command(
            alias,
            f"/api/dashboards/uid/{dashboard_uid}",
            options={"method": "DELETE"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_users(self, alias: str, **kwargs) -> list:
        """
        Get all users (requires admin permissions).

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            list: List of users.
        """
        response = self.execute_command(alias, "/api/users", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_current_user(self, alias: str, **kwargs) -> dict:
        """
        Get the current authenticated user.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            dict: Current user information.
        """
        response = self.execute_command(alias, "/api/user", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_organizations(self, alias: str, **kwargs) -> list:
        """
        Get all organizations (requires admin permissions).

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            list: List of organizations.
        """
        response = self.execute_command(alias, "/api/orgs", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_current_organization(self, alias: str, **kwargs) -> dict:
        """
        Get the current organization.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            dict: Current organization information.
        """
        response = self.execute_command(alias, "/api/org", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_folders(self, alias: str, **kwargs) -> list:
        """
        Get all folders.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            list: List of folders.
        """
        response = self.execute_command(alias, "/api/folders", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def get_alerts(self, alias: str, **kwargs) -> list:
        """
        Get all alerts.

        Args:
            alias (str): The session alias for the Grafana connection.

        Returns:
            list: List of alerts.
        """
        response = self.execute_command(alias, "/api/alerts", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())
