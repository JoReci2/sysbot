"""
Helper Utilities Module

This module provides various helper classes and utility functions for SysBot,
including Windows CIM helpers, timezone conversion utilities, and security-related
operations such as certificate information retrieval.
"""
import datetime
import socket
import ssl
import pytz
from OpenSSL import crypto


class Windows:
    @staticmethod
    def get_cim_class(namespace: str, classname: str, property: str) -> dict:
        return f"Get-CimInstance -Namespace {namespace} -ClassName {classname} | Select-Object {property} | ConvertTo-Json"


class Timezone:
    """
    Utility class for timezone operations.
    """

    @staticmethod
    def convert_to_offset(timezone: str) -> str:
        try:
            tz = pytz.timezone(timezone)
            dt = datetime.datetime.now(tz)
            offset = dt.strftime("%z")
            formatted_offset = offset[:3] + ':' + offset[3:]
            return formatted_offset
        except pytz.UnknownTimeZoneError:
            raise pytz.UnknownTimeZoneError(f"Unknown timezone: {timezone}")
        except Exception as e:
            raise Exception(f"Failed to convert timezone to offset: {str(e)}") from e


class Security:
    """
    Utility class for security-related operations.
    """

    def __init__(self, sysbot_instance):
        """
        Initialize Security class with a Sysbot instance.

        Args:
            sysbot_instance: Instance of the Sysbot class
        """
        self._sysbot = sysbot_instance

    def get_certificate_informations(self, host: str, port: int, tunnel=None) -> dict:
        """
        Get information about web service certificate.

        Args:
            host (str): The hostname or IP address
            port (int): The port number
            tunnel: Optional tunnel configuration

        Returns:
            dict: Dictionary containing certificate information including:
                - Country: Subject country
                - Region: Subject region/state
                - Locality: Subject locality
                - Organization: Subject organization
                - Common Name: Subject common name
                - Serial Number: Certificate serial number
                - Version: Certificate version
                - Algorithm: Signature algorithm
                - Validity Period: Certificate expiration date
                - Fingerprint: SHA256 fingerprint
                - Issuer: Issuer common name

        Raises:
            Exception: If certificate retrieval or parsing fails
        """
        self._sysbot.open_session('get_certificate', 'socket', 'tcp', host, port, tunnel)
        try:
            try:
                der_cert = self._sysbot._cache.connections.switch('get_certificate')['session'].getpeercert(True)
            except ssl.SSLError as e:
                raise Exception(f"Failed to retrieve certificate: {str(e)}")
            except socket.error as e:
                raise Exception(f"Socket error while retrieving certificate: {str(e)}")
            except Exception as e:
                raise Exception(f"Unexpected error while retrieving certificate: {str(e)}")
            try:
                certificate = ssl.DER_cert_to_PEM_cert(der_cert)
                x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
                issuer = {k.decode(): v.decode() for k, v in x509.get_issuer().get_components()}
                subject = {k.decode(): v.decode() for k, v in x509.get_subject().get_components()}
                serial_number = x509.get_serial_number()
                version = x509.get_version()
                algo = x509.get_signature_algorithm().decode()
                not_after = datetime.datetime.strptime(x509.get_notAfter().decode(), "%Y%m%d%H%M%SZ")
                fingerprint = x509.digest("sha256").decode()

                cert_info = {
                    "Country": subject.get("C", "N/A"),
                    "Region": subject.get("ST", "N/A"),
                    "Locality": subject.get("L", "N/A"),
                    "Organization": subject.get("O", "N/A"),
                    "Common Name": subject.get("CN", "N/A"),
                    "Serial Number": serial_number,
                    "Version": version,
                    "Algorithm": algo,
                    "Validity Period": not_after,
                    "Fingerprint": fingerprint,
                    "Issuer": issuer.get('CN', 'N/A')
                }

                return cert_info
            except Exception as e:
                raise Exception(f"Failed to get certificate informations: {str(e)}")
        finally:
            self._sysbot.close_session('get_certificate')
