# Server Umzug: Fake Check App - User Guide

## 1. Voraussetzungen & DNS Einstellungen (Domain)
Die Anwendung nutzt die Domain **lui-inventions.com** (sowie ggf. Subdomains wie **start.lui-inventions.com** oder **www.lui-inventions.com**). 
Bevor das Projekt auf dem neuen Server per HTTPS (SSL/TLS) erreichbar ist, musst du die IP-Adresse im DNS auf den neuen Server abändern.

1. Logge dich bei deinem Domain-Provider ein (z.B. Cloudflare, Strato, Namecheap, INWX).
2. Gehe in die DNS-Einstellungen für die Domain `lui-inventions.com`.
3. Ändere die folgenden **A-Records** so ab, dass sie auf die **IP-Adresse deines NEUEN Servers** (IPv4) zeigen:
   - Name: `@` (Root/Leer) -> Wert: `[NEUE_SERVER_IP]`
   - Name: `www` -> Wert: `[NEUE_SERVER_IP]`
   - Name: `start` -> Wert: `[NEUE_SERVER_IP]`
4. *(Optional)* Falls du auch AAAA-Records (IPv6) hast, passe diese auf die IPv6 deines neuen Servers an oder lösche sie vorerst, falls du auf dem neuen Server keine IPv6 nutzt.
5. Speichere die Änderungen. (Achtung: Bis die DNS-Updates weltweit übernommen sind, kann es 5-60 Minuten dauern).

## 2. Projekt vom aktuellen auf den neuen Server kopieren
Um den gesamten Projektordner sicher und verlustfrei zu kopieren, nutzen wir `rsync`.

Führe den folgenden Befehl auf deinem **aktuellen/alten Server** aus. Ersetze dabei `[NEUE_SERVER_IP]` durch die tatsächliche IP des neuen Servers:

```bash
rsync -avz --progress "/home/serveradmin/Fake Check App" root@[NEUE_SERVER_IP]:/home/serveradmin/
```

*Warum so? Dieser Befehl kopiert den gesamten Ordner inkl. Dateien wie `docker-compose.yml`, Quellcode und – extrem wichtig – alle versteckten Dateien (wie die `.env`, in der deine Datenbank-Credentials, OpenAI- und RapidAPI-Keys stehen, sowie die `cookies.txt`).*

## 3. Den KI-Agenten auf dem neuen Server starten
Jetzt, da die Dateien drüben sind, müssen wir den neuen Server konfigurieren.

1. Verbinde dich per SSH mit deinem **neuen** Server (`ssh root@[NEUE_SERVER_IP]`).
2. Starte dort deinen KI-Agenten (Claude Code).
3. Öffne (z.B. per Editor oder Cat) die Datei `agenteinrichtung.md`, welche durch den rsync-Befehl nun unter `/home/serveradmin/Fake Check App/fakecheck/agenteinrichtung.md` liegt, und kopiere den gesamten Text in deine Zwischenablage.
4. Füge diesen Text als deinen ersten, großen Prompt (Anweisung) in den KI-Agenten auf dem neuen Server ein und schicke ihn ab.
5. Lehn dich zurück. Der Agent wird nun vollautomatisch:
   - Docker und Docker-Compose installieren
   - Deine Docker-Container (Backend, Frontend, Redis, Worker, Nginx) bauen und starten
   - Deinen bestehenden Caddy-Webserver so einstellen, dass deine Domain `lui-inventions.com` direkt per HTTPS auf dein App-Frontend (Port 8085) geleitet wird.
