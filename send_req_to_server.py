import socket
import ssl
import os
from subprocess import run

# IMPORTANT README
#
# IN ORDER TO WORK, WE NEED THE FOLLOWING FILES IN THE CURRENT DIR:
# - publickey - containing the public key configured with wg
# - wireguard_config_ip - containing the ip address configured with wg for the VPN
# - the wg0.cfg config file (in /etc/wireguard/wg0.cfg) that sets up wireguard on the client side

def create_ssl_client(server_host, server_port, public_key_file):
    # Create a context for the SSL client
    context = ssl.create_default_context()

    # For a self-signed certificate, you can choose to skip verification
    # In a production environment with a valid certificate, this should not be done
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Read the public key from file
    with open(public_key_file, 'rb') as file:
        public_key = file.read()

    with open(wireguard_cfg, 'rb') as file:
        cfg_ip = file.read()

    # Create a socket and wrap it in an SSL context
    with socket.create_connection((server_host, server_port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_host) as ssock:
            # Send the public key to the server
            ssock.sendall(public_key)
            ssock.sendall(cfg_ip)
            data = ssock.recv(1024)
            print(f'Received: {data.decode()}')
            data_start_wireguard = ssock.recv(1024)
            print(f'we received somethig, wonder what it is {data_start_wireguard}')
# Path to the public key file
public_key_file = os.path.join(os.path.dirname(__file__), 'publickey')

wireguard_cfg = os.path.join(os.path.dirname(__file__), 'wireguard_config_ip')

# Replace with your server's hostname and SSL port
create_ssl_client('165.22.64.146', 443, public_key_file)

# Run wireguard
run(["wg-quick", "up", "wg0"])
