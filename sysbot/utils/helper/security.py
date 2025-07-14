from OpenSSL import crypto
import ssl, socket, datetime

class Security(object):
    
    def get_certificate_informations(self, session) -> dict[str, str]:
        """
        get infomations about web service certificate.
        """
        try:
            der_cert = session.getpeercert(True)
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
                "Fingerprint": fingerprint
            }

            return cert_info
        except Exception as e:
            raise Exception(f"Failed to get certificate informations: {str(e)}")