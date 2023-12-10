# zero-trust-express

## Usage

IN ORDER TO WORK, WE NEED THE FOLLOWING FILES IN THE CURRENT DIR:

- publickey - containing the public key configured with wg
- wireguard_config_ip - containing the ip address configured with wg for the VPN
- the wg0.cfg config file (in /etc/wireguard/wg0.cfg) that sets up wireguard on the client side

Make sure server is up and running, listening for connections. Run 'python3 send_req_to_server.py' to send a request to the server, containing client's desired ip address and public key. The server will respond with success of failure.

In order to work properly, the server also has its own config file.

Server IP Address: 165.22.64.146

Wireguard Server Port: 51820

Server Public Key: 9AIcnYJ0R/4iT1o6WB+GKHOEhjkHy+o24pbW3g7Jrnk=
