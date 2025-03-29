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

from OpenSSL import crypto
import ssl, socket, datetime

class Security(object):
    
    def get_certificate_informations(self, host: str, port: int) -> dict[str, str]:
        """
        get infomations about web service certificate.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = socket.create_connection((host, port))
        sock = context.wrap_socket(conn, server_hostname=host)
        sock.settimeout(10)
        try:
            der_cert = sock.getpeercert(True)
        finally:
            sock.close()
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