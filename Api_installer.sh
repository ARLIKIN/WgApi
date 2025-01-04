#!/bin/bash

RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m'

function isRoot() {
	if [ "${EUID}" -ne 0 ]; then
		echo "Neobhodimo zapustit' skript ot root pol'zovatelya!!!"
		exit 1
	fi
}

function checkVirt() {
	if [ "$(systemd-detect-virt)" == "openvz" ]; then
		echo "OpenVZ is not supported"
		exit 1
	fi

	if [ "$(systemd-detect-virt)" == "lxc" ]; then
		echo "LXC is not supported (yet)."
		echo "WireGuard can technically run in an LXC container,"
		echo "but the kernel module has to be installed on the host,"
		echo "the container has to be run with some specific parameters"
		echo "and only the tools need to be installed in the container."
		exit 1
	fi
}

function checkOS() {
	# Check OS version
	if [[ -e /etc/debian_version ]]; then
		source /etc/os-release
		OS="${ID}" # debian or ubuntu
		if [[ ${ID} == "debian" || ${ID} == "raspbian" ]]; then
			if [[ ${VERSION_ID} -lt 10 ]]; then
				echo "Ваша версия Debian (${VERSION_ID}) не поддерживается. Пожалуйста используйте Debian 10 Buster или ниже"
				exit 1
			fi
			OS=debian # overwrite if raspbian
		fi
	elif [[ -e /etc/fedora-release ]]; then
		source /etc/os-release
		OS="${ID}"
	elif [[ -e /etc/centos-release ]]; then
		source /etc/os-release
		OS=centos
	elif [[ -e /etc/oracle-release ]]; then
		source /etc/os-release
		OS=oracle
	elif [[ -e /etc/arch-release ]]; then
		OS=arch
	else
		echo "Looks like you aren't running this installer on a Debian, Ubuntu, Fedora, CentOS, Oracle or Arch Linux system"
		exit 1
	fi
}

function initialCheck() {
	isRoot
	checkVirt
	checkOS
}

function installQuestions() {
	echo "Dobro pozhalovat' v ustanovshchik API WireGuard!"
	echo ""
  read -rp "input username: " -e ADMIN_USERNAME
  read -rp "input password: " -e ADMIN_PASSWORD
  FLASK_HOST=$(ip -4 addr | sed -ne 's|^.* inet \([^/]*\)/.* scope global.*$|\1|p' | awk '{print $1}' | head -1)
  if [[ -z ${FLASK_HOST} ]]; then
    # Detect public IPv6 address
    FLASK_HOST=$(ip -6 addr | sed -ne 's|^.* inet6 \([^/]*\)/.* scope global.*$|\1|p' | head -1)
  fi
  read -rp "input host panel: " -e -i "${FLASK_HOST}" FLASK_HOST
  read -rp "input port panel: " -e FLASK_PORT
	echo ""
	echo "Otlichno vse osnovnye danny vvedeny!"
	read -n1 -r -p "Press any key..."
}

function installWireGuard() {
	# Run setup questions first
	installQuestions

	# Install WireGuard tools and module
	if [[ ${OS} == 'ubuntu' ]] || [[ ${OS} == 'debian' && ${VERSION_ID} -gt 10 ]]; then

		export TZ=Europe/Moscow
		apt-get update
			apt-get install unzip
			apt-get install python3-pip -y
			wget https://github.com/ARLIKIN/WgApi/archive/refs/heads/main.zip
			unzip main.zip
			rm main.zip
			pip install -r "$(pwd)/WgApi-main/requirements.txt"
			echo "FLASK_HOST=${FLASK_HOST}
      FLASK_PORT=${FLASK_PORT}
      ADMIN_USERNAME=${ADMIN_USERNAME}
      ADMIN_PASSWORD=${ADMIN_PASSWORD}" >"$(pwd)/WgApi-main/.env"
          chmod 744 -R $(pwd)/WgApi-main/
          echo "[Unit]
      Description=api for Wireguard
      After=multi-user.target

      [Service]
      Type=simple
      Restart=always
      RestartSec=15
      WorkingDirectory=$(pwd)/WgApi-main
      ExecStart=/usr/bin/python3 $(pwd)/WgApi-main/app.py
      User=root

      [Install]
      WantedBy=multi-user.target">"/etc/systemd/system/ApiWg.service"
			systemctl daemon-reload
			sudo systemctl enable ApiWg.service
			clear
			echo "Installed API"
		fi
}

# Check for root, virt, OS...
initialCheck

installWireGuard