import socket
import ssl
import subprocess
import requests
import time
import jwt
from subprocess import run

import json

def save_db_to_file(db, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(db, file)
        print(f"Database saved to {filename}.")

def load_db_from_file(filename):
    try:
        with open(filename, 'r') as file:
            print(f'Database loaded: {db}')
            return json.load(file)
    except FileNotFoundError:
        print(f"No such file: {filename}")
        return {}  # Return an empty dictionary if file not found


# Auth0 credentials and endpoints
AUTH0_DOMAIN = 'dev-zl27wopcwlh36x66.us.auth0.com'  # Replace with your Auth0 domain
CLIENT_ID = 'QWPwOiVJ0K4OkUkhv9U4gpYmhMVWTOcC'  # Replace with your Auth0 application's client ID

db = {}

# Function to add a user
def add_user(name, email, token):
    if email in db:
        print("User already exists.")
    else:
        db[email] = {'name': name, 'email': email, 'token' : token}
        print("User added.")

# Function to get a user's information
def get_user(user_id):
    return db.get(email, "User not found.")

def user_exists(email):
    return email in db

# Function to delete a user
def delete_user(email):
    if email in db:
        del db[email]
        print("User deleted.")
    else:
        print("User not found.")

def get_device_code():
    url = f'https://{AUTH0_DOMAIN}/oauth/device/code'
    payload = {
        'client_id': CLIENT_ID,
        'scope': 'openid profile email',  # Adjust scopes as needed
        #'audience': 'YOUR_API_AUDIENCE'  # Replace with your API identifier, if needed
    }
    response = requests.post(url, data=payload)
    print("Response from Auth0:", response.text)
    response.raise_for_status()
    return response.json()


def poll_for_token(device_code):
    url = f'https://{AUTH0_DOMAIN}/oauth/token'
    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code,
        'client_id': CLIENT_ID
    }
    while True:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400 and response.json().get('error') == 'authorization_pending':
            print("Waiting for user authorization...")
            time.sleep(5)  # Poll every 5 seconds as specified by Auth0
        else:
            print('Error polling for token:', response.text)
            # break  # Exit the loop if a different error occurs



def create_server(host="0.0.0.0", port=443):
    # load database from file
    db = load_db_from_file("database.json")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Ensure correct file paths for your certificate and private key
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((host, port))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            good = 0
            while True:  # Keep the server running to accept multiple connections
                conn, addr = ssock.accept()
                print(f"Connection from {addr} has been established.")
                # Receive data from the client
                data = conn.recv(1024)
                print(f'Received from client: {data.decode()}')
                        # Get IP and public key
                #ip = addr[0]
                publicKey = data.decode()

                # Receive ip addr from client
                data_ip = conn.recv(1024)
                print(f'Received from client ip: {data_ip}')
                ip = data_ip
                # Add to VPN environment received entry

                try:
                    auth0_response = get_device_code()
                    response = f"Please go to {auth0_response['verification_uri_complete']} and enter the code: {auth0_response['user_code']}"
                except Exception as e:
                    response = f'Error in Auth0 Device Authorization: {str(e)}'

                conn.sendall(response.encode())
                # print("sent everything!!!!!!!!!!!!!!!!!")
                token_response = poll_for_token(auth0_response['device_code'])
                access_token = token_response['access_token']
                id_token = token_response['id_token']

                decoded_token = jwt.decode(id_token, options={"verify_signature": False})

                # Accessing the email claim
                email = decoded_token.get('email')
                name = decoded_token.get('name')

                # check if player is in db = {}
                #if user_exists(email):
                #    # ignore entry - user already here
                #    print("User already in here!")
                #    # user is waiting for a response - notify login fail
                #    conn.sendall(b'USER ALREADY IN THE SYSTEM')
                #    conn.close()
                #    continue
                
                add_user(name, email, token)
                
                print(f'New login: {name} - {email}')

                #print("Access token:", access_token)
                process = subprocess.Popen(['/home/connection_trial/add_new_vpn_entry.sh', ip, publicKey], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

                #print("STDOUT:", stdout)
                #print("STDERR:", stderr)
                conn.sendall(b'LOGIN SUCCESFUL')
                conn.close()

                #debug print database
                for entry in db:
                    print(entry)

                # save database to file
                save_db_to_file(db, "database.json")
                break
# Run WireGuard
run(["wg-quick", "up", "wg0"])

# Update the file paths to your certificate and key, then start the server
create_server(host="0.0.0.0", port=443)
