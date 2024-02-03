from library.variables import logging
import http.server, socketserver, ssl
import datetime
import sys
import os

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID


def generate_ssl(certfile_dir, keyfile_dir, hostname="localhost"):
    # Generate a self-signed certificate if it doesn't exist
    if not os.path.isfile(certfile_dir) or not os.path.isfile(keyfile_dir):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        os.makedirs(os.path.dirname(certfile_dir), exist_ok=True)

        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(hostname)),
        ])

        cert = x509.CertificateBuilder().subject_name(
            name
        ).issuer_name(
            name
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(key, hashes.SHA256())

        # Write our certificate out to disk.
        with open(certfile_dir, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write our key out to disk
        with open(keyfile_dir, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

class gui:
    def run(PublicMode=False, port=8080, allow_dir_listing=False):
        debug = False
        if PublicMode:
            os.makedirs('library/ssl', exist_ok=True)
        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = "library/WebGUI/content/"
                super().__init__(*args, directory=self.content_directory, **kwargs)

            def add_security_headers(self):
                # Add security headers based on user configuration
                csp_directives = ["Content-Security-Policy", "default-src 'self';","script-src 'self';","style-src 'self';","img-src 'self';","font-src 'self'"]
                self.send_header("Content-Security-Policy", csp_directives)
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

            def do_GET(self):
                self.log_request_action()
                if not PublicMode:
                    # If the request is not from localhost, return a 403
                    if self.client_address[0] != "127.0.0.1":
                        self.send_error(403, "Forbidden", "External IP addresses are not allowed")
                        return
                else:
                    # If the request is from localhost and thats not allowed, return a 403
                    if self.client_address[0] == "127.0.0.1":
                        self.send_error(403, "Forbidden", "Localhost is not allowed. Use domain to access instead")
                        return

                # TODO: Warden will be replaced with UserMan Website access permissions later.

                # Handle directory listing.
                if not allow_dir_listing:
                    if self.path.endswith("/"):
                        # If the path is a directory and not the root, return a 403
                        if self.path != "/":
                            self.send_error(403, "Directory listing is disabled", "Directory Listing is Forcefully disabled")
                            return

                # Check if the requested path is the root directory
                if self.path == "/":
                    # Serve the default_index as the landing page
                    # Get the absolute path of the default index file
                    default_index_path = os.path.abspath(os.path.join(self.content_directory, "index.html"))
                    
                    # Check if the default index file exists
                    if os.path.exists(default_index_path):
                        # Open the default index file and read its content
                        with open(default_index_path, 'rb') as index_file:
                            content = index_file.read()
                            
                            # Send a HTTP 200 OK response
                            self.send_response(200)
                            
                            # Set the Content-Type header to text/html
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            
                            # Write the content to the response body
                            self.wfile.write(content)
                else:
                    # If the requested path is not the root directory
                    # Get the absolute path of the requested file
                    requested_file_path = os.path.abspath(os.path.join(self.content_directory, self.path.strip('/')))
                    
                    # Check if the requested file exists
                    if os.path.exists(requested_file_path):
                        # If the requested file exists, call the parent class's do_GET method
                        super().do_GET()
                        return True
                    else:
                        # Get the absolute path of the custom 404 page
                        notfoundpage_path = os.path.abspath(os.path.join(self.content_directory, "404.html"))
                        # Check if the custom 404 page exists
                        if os.path.exists(notfoundpage_path):
                            # Open the custom 404 page and read its content
                            with open(notfoundpage_path, 'rb') as notfoundpage_file:
                                content = notfoundpage_file.read()
                                self.send_response(404)
                                # Set the Content-Type header to text/html
                                self.send_header("Content-type", "text/html")
                                self.end_headers()
                                
                                # Write the content to the response body
                                self.wfile.write(content)
                        else:
                            # Raise 404 error if the custom 404 page doesn't exist
                            self.send_error(404, "File not found", "The requested file was not found")
                            return

                    # Send the HTML content as a response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content)

            def log_request_action(self):
                # Get client address and requested file
                client_address = self.client_address[0]
                requested_file = self.path
                # Open the log file and write the request information
                if requested_file == "/":
                    logging.info(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested {requested_file} (the landing page)\n")
                else:
                    logging.info(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested file {requested_file}\n")

        # Redirect stdout and stderr to /dev/null if silent is True
        if not debug:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            if PublicMode is True:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                cert_dir = os.path.abspath('library/ssl/webgui-api.pem')
                private_dir = os.path.abspath('library/ssl/webgui-api.key')

                generate_ssl(cert_dir, private_dir)

                context.load_cert_chain(cert_dir, private_dir)
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                logging.info(f"WebGUI is running with SSL.")
            else:
                logging.info(f"WebGUI is running without SSL.")

            # Start the server and keep it running until interrupted
            logging.info(f"WebGUI is now running on port {port}")
            httpd.serve_forever()
            # Once it reaches here, it stops.
            logging.info("WebGUI has been stopped.")
            return True