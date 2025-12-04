"""Tests for PowerDNS client."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from ultahost_dns.powerdns_client import PowerDNSClient


class TestPowerDNSClient:
    """Test PowerDNS API client."""

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_create_zone(self, mock_session_class):
        """Test zone creation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.create_zone("example.com")

        assert result is True
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/zones" in call_args[1]["url"]

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_delete_zone(self, mock_session_class):
        """Test zone deletion."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.delete_zone("example.com")

        assert result is True
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "DELETE"

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_add_record(self, mock_session_class):
        """Test adding DNS record."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.add_record("example.com", "www", "A", "192.168.1.1")

        assert result is True
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "PATCH"
        assert "rrsets" in call_args[1]["json"]

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_delete_record(self, mock_session_class):
        """Test deleting DNS record."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.delete_record("example.com", "www", "A")

        assert result is True
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "PATCH"

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_test_connection(self, mock_session_class):
        """Test connection test."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.test_connection()

        assert result is True

    @patch("ultahost_dns.powerdns_client.requests.Session")
    def test_test_connection_failure(self, mock_session_class):
        """Test connection test failure."""
        mock_session = MagicMock()
        mock_session.request.side_effect = requests.exceptions.RequestException("Connection failed")
        mock_session_class.return_value = mock_session

        client = PowerDNSClient(api_url="https://dns.example.com", api_key="test-key")
        result = client.test_connection()

        assert result is False


