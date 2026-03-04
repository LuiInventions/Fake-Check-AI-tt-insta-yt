# Agenten Ausführungsplan für den neuen Server
Ich habe das Projekt "Fake Check App" manuell in den Ordner `/home/serveradmin/Fake Check App/fakecheck/` kopiert. Das Ziel ist es, diese Anwendung auf diesem leeren Server komplett zum Laufen zu bringen.

**Wichtig: Die Zieldomain lautet `lui-inventions.com` (Subdomains wie `start.lui-inventions.com` oder `www.lui-inventions.com` müssen ggf. ebenfalls bedacht werden, falls im Caddyfile gesondert aufgeführt).**

Hier ist dein strikter Ausführungsplan. Führe erst Statuschecks durch, bevor du Tools installierst oder Konfigurationen änderst.

---

### Layer 1: Systemanalyse & Voraussetzungen prüfen
1. Prüfe, ob der Ordner `/home/serveradmin/Fake Check App/fakecheck/` existiert (`ls -la "/home/serveradmin/Fake Check App/fakecheck/"`). Kontrolliere zwingend, ob die Dateien `.env`, `docker-compose.yml` und `cookies.txt` vorhanden sind.
2. Prüfe, ob Docker und Docker-Compose installiert sind (`docker -v`, `docker-compose -v`).
3. Prüfe, ob die Ports `8000` (Backend), `3000` (Frontend) und `8085` (Nginx/Internal) auf dem System frei sind (`ss -tlnp`).

### Layer 2: Installation & Container Launch
1. Falls Docker nicht installiert ist, installiere es via `sudo apt-get update && sudo apt-get install -y docker.io docker-compose`.
2. Aktiviere und starte den Docker Daemon: `sudo systemctl enable --now docker`.
3. Navigiere in das Verzeichnis: `cd "/home/serveradmin/Fake Check App/fakecheck/"`
4. Starte die Applikation: `docker-compose up -d --build`.
5. Warte ca. 15-20 Sekunden. Prüfe dann den Status der Container (`docker ps`). Stelle sicher, dass Container wie `fakecheck-nginx`, `fakecheck-frontend`, `fakecheck-backend`, `fakecheck-worker` und `fakecheck-redis` im Status "Up" sind.
6. Prüfe lokal, ob der Nginx Proxy innerhalb von Docker erfolgreich auf Port 8085 antwortet: `curl -I 127.0.0.1:8085`.

### Layer 3: Caddy Reverse Proxy & Routing Einrichten
Du sollst Caddy so konfigurieren, dass externe Anfragen für `lui-inventions.com` (sowie `www.lui-inventions.com` und `start.lui-inventions.com`) per HTTPS an den internen Nginx-Port `8085` weitergeleitet werden. 
Befolge dazu STRIKT diese "# Caddy & URL Reliability Rules":
1. **Never Overwrite**: Niemals das vorhandene Caddyfile komplett ersetzen. Nutze `replace_file_content`, um es präzise zu bearbeiten. Lies zuerst `/home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile`.
2. **Backup First**: Bevor du etwas änderst, erstelle ein Backup: `cp /home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile /home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile.bak.$(date +%Y%m%d_%H%M%S)`
3. Füge folgenden Block an einer passenden Stelle (nach eventuellen globalen Blöcken) in das Caddyfile ein:
   ```caddyfile
   lui-inventions.com, www.lui-inventions.com, start.lui-inventions.com {
       reverse_proxy 127.0.0.1:8085
   }
   ```
4. **Validate Before Reload**: Führe `caddy validate --config /home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile` aus. Behebe eventuelle Syntaxfehler sofort vor dem Reload!
5. **Caddy Reload**: Aktiviere die Einstellungen durch: `caddy reload --config /home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile`
6. **Connectivity Gate**: Teste lokal die Anbindung per `curl -I -k --resolve lui-inventions.com:443:127.0.0.1 https://lui-inventions.com`. Der HTTP Status (z.B. 200, 307 etc.) muss zurückkommen.

### Troubleshooting & Rollback (Falls Fehler auftreten)
- Falls `docker-compose` Buildfehler wirft: Nutze `docker logs fakecheck-backend` (bzw. für den betroffenen Container), um den Traceback zu analysieren.
- Falls Caddy nicht startet / Validierung fehlschlägt: Stelle das Backup mit `cp Caddyfile.bak... Caddyfile` wieder her und führe `caddy reload` aus. Finde den Fehler im Caddyfile und korrigiere ihn.

Bitte bestätige kurz, wenn du diesen Plan beginnst und arbeite ihn dann strikt ab.
