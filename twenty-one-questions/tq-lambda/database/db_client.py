"""
Database client for connecting to RDS PostgreSQL database.
"""

import os
import json
import psycopg2
from psycopg2 import pool
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError


class DatabaseClient:
    """Client for managing database connections to RDS PostgreSQL."""

    def __init__(self):
        """Initialize the database client with connection parameters from environment."""
        self.db_secret_arn = os.getenv("DB_SECRET_ARN")
        self.db_endpoint = os.getenv("DB_ENDPOINT")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "aiplaygrounddb")
        self._connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self._secrets_client = boto3.client("secretsmanager")

    def _get_db_credentials(self) -> Dict[str, str]:
        """
        Retrieve database credentials from AWS Secrets Manager.

        Returns:
            dict: Database credentials containing username and password

        Raises:
            ClientError: If unable to retrieve secret from Secrets Manager
            KeyError: If required keys are missing from secret
        """
        try:
            response = self._secrets_client.get_secret_value(SecretId=self.db_secret_arn)
            secret_string = response["SecretString"]
            credentials = json.loads(secret_string)
            return {
                "username": credentials["username"],
                "password": credentials["password"],
            }
        except ClientError as e:
            raise Exception(f"Failed to retrieve database credentials: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Invalid secret format: {str(e)}")

    def get_connection(self):
        """
        Get a database connection.

        Returns:
            psycopg2.connection: Database connection object

        Raises:
            Exception: If connection fails
        """
        credentials = self._get_db_credentials()

        try:
            conn = psycopg2.connect(
                host=self.db_endpoint,
                port=self.db_port,
                database=self.db_name,
                user=credentials["username"],
                password=credentials["password"],
                connect_timeout=10,
            )
            return conn
        except psycopg2.Error as e:
            raise Exception(f"Failed to connect to database: {str(e)}")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Optional tuple of parameters for parameterized query

        Returns:
            list: Query results as list of tuples

        Raises:
            Exception: If query execution fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except psycopg2.Error as e:
            raise Exception(f"Query execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    def execute_update(
        self, query: str, params: Optional[tuple] = None
    ) -> Optional[int]:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query string
            params: Optional tuple of parameters for parameterized query

        Returns:
            int: Number of rows affected, or None if not applicable

        Raises:
            Exception: If query execution fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Update execution failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    def execute_transaction(self, queries: list) -> bool:
        """
        Execute multiple queries in a transaction.

        Args:
            queries: List of (query, params) tuples

        Returns:
            bool: True if transaction succeeded, False otherwise

        Raises:
            Exception: If transaction fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            for query, params in queries:
                cursor.execute(query, params or ())
            conn.commit()
            cursor.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Transaction failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    def test_connection(self) -> bool:
        """
        Test the database connection.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False


# Singleton instance for reuse across Lambda invocations
_db_client: Optional[DatabaseClient] = None


def get_db_client() -> DatabaseClient:
    """
    Get or create a singleton database client instance.

    Returns:
        DatabaseClient: Database client instance
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client

