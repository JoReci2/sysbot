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
        """
        Converts the provided timezone to an offset.

        Args:
            timezone (str): The timezone name (e.g., 'America/New_York', 'Europe/Paris')

        Returns:
            str: The timezone offset in format '+HH:MM' or '-HH:MM'

        Raises:
            pytz.UnknownTimeZoneError: If the timezone is unknown
            Exception: If conversion fails
        """
        try:
            tz = pytz.timezone(timezone)
            dt = datetime.datetime.now(tz)
            offset = dt.strftime("%z")
            formatted_offset = offset[:3] + ':' + offset[3:]
            return formatted_offset
        except pytz.UnknownTimeZoneError as e:
            raise pytz.UnknownTimeZoneError(f"Unknown timezone: {timezone}")
        except Exception as e:
            raise Exception(f"Failed to convert timezone to offset: {str(e)}")


class Security:
    """
    Utility class for security-related operations.
    """

    @staticmethod
    def get_certificate_informations(host: str, port: int, timeout: int = 30) -> dict:
        """
        Get information about web service certificate.

        Args:
            host (str): The hostname or IP address
            port (int): The port number
            timeout (int): Connection timeout in seconds (default: 30)

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
        sock = None
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Create socket and wrap with SSL
            sock = socket.create_connection((host, port), timeout=timeout)
            ssl_sock = context.wrap_socket(sock, server_hostname=host)

            try:
                der_cert = ssl_sock.getpeercert(True)
            except ssl.SSLError as e:
                raise Exception(f"Failed to retrieve certificate: {str(e)}")
            except socket.error as e:
                raise Exception(f"Socket error while retrieving certificate: {str(e)}")
            finally:
                ssl_sock.close()

        except socket.timeout:
            raise Exception(f"Connection to {host}:{port} timed out")
        except socket.gaierror as e:
            raise Exception(f"Failed to resolve hostname {host}: {str(e)}")
        except ConnectionRefusedError:
            raise Exception(f"Connection refused to {host}:{port}")
        except Exception as e:
            if sock:
                sock.close()
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
