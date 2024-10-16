#!/bin/bash

source /etc/wireguard/params

function revokeClient() {
	CLIENT_NAME="$1"
	HOME="/root/VPNHubBot/WG/files"
	sed -i "/^### Client ${CLIENT_NAME}\$/,/^$/d" "/etc/wireguard/${SERVER_WG_NIC}.conf"
	rm -f "${HOME}/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"
	wg syncconf "${SERVER_WG_NIC}" <(wg-quick strip "${SERVER_WG_NIC}")
  echo "okey"
}

revokeClient "$1"