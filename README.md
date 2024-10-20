# Wireguard API

<h2>Quick installation:</h2>

```bash
sudo wget https://github.com/ARLIKIN/WgApi/releases/download/download/Wireguard-installer-with-Adminpanel.sh && chmod 774 Wireguard-installer-with-Adminpanel.sh && ./Wireguard-installer-with-Adminpanel.sh
```
- after configuring the wg, a choice will appear: `Hotite li ustanovit' srazu API(1 - Da, 0 - Net)::` We agree (press 1)

<h3>Сhecking the operation of the service</h3>

```bash
sudo systemctl status ApiWg
```

<h3>Start</h3>

```bash
sudo systemctl start ApiWg
```

<h3>Stop</h3>

```bash
sudo systemctl stop ApiWg
```

<h3>Restart</h3>

```bash
sudo systemctl restart ApiWg
```