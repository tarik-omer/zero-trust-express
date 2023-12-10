#!/bin/bash
# Script to create a new VPN connection - creates keys and updates the config file for WireGuard

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Check if the user provided an IP address and a public key
if [ -z "$1" ]
  then echo "Please provide an IP address"
  exit
fi

if [ -z "$2" ]
  then echo "Please provide a public key"
  exit
fi

# Get the public key of the client
publickey_client=$2

# Get the IP address of the new VPN connection
ip_address=$1

# Stop WireGuard
wg-quick down wg0

# Update the config file for WireGuard
echo "
[Peer]
PublicKey = $publickey_client
AllowedIPs = $ip_address/32
" >> /etc/wireguard/wg0.conf

# Restart WireGuard
wg-quick up wg0
