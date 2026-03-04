A) TL;DR
Dieser Plan beschreibt die genauen Schritte, um das bestehende Web-Projekt (FakeCheck / Storefront) in eine native mobile App (iOS & Android) umzuwandeln. Wir nutzen dafür **CapacitorJS**, da es die bestehenden Web-Technologien (Next.js/React) verwendet und ohne großen Aufwand native Wrapper erzeugt. Im ersten Schritt bereiten wir das Web-Projekt für den statischen Export vor. Danach initialisieren wir Capacitor, fügen die Plattformen Android und iOS hinzu und bereiten den Prozess für internes Testing (Apple TestFlight / Google Play Internal Testing) vor.

B) Goal & Non-Goals
**Goal**: 
- Das Web-Frontend als native iOS- und Android-App-Basis vorbereiten.
- Capacitor in das bestehende Frontend-Verzeichnis integrieren.
- Erstellung einer detaillierten Anleitung für das Testing auf dem Handy (TestFlight / Play Console).
**Non-Goals**: 
- Native UI-Komponenten von Grund auf neu in Swift/Kotlin schreiben (die App lädt das Web-Frontend nativ).
- Vollautomatischer Upload in den App Store durch Claude (dafür werden Entwickler-Accounts, lokale Zertifikate und Xcode auf einem Mac benötigt, was manuell durch den User und nicht auf dem Linux-Server erfolgen muss).

C) Context for Claude Code
Du bist Claude Code und setzt diesen Plan 1:1 um. Das Projekt beinhaltet ein Web-Frontend. Du modifizierst die `next.config.mjs` (oder `.js`) für den statischen „export“ Mode, fügst die Abhängigkeiten `@capacitor/cli` und `@capacitor/core` hinzu und generierst die nativen Projekte (`android/` und `ios/`). Anschließend schreibst du eine ausführliche Markdown-Anleitung für den User (die Schritt-für-Schritt-Erklärung, wie er diese Ordner auf seinen PC lädt, in Android Studio/Xcode öffnet, auf dem Smartphone testet und in die App-Stores hochlädt).

D) Project Status Check
- `cd /home/serveradmin/Training/training/storefront` (bzw. das korrekte Frontend-Verzeichnis der App).
- `cat package.json` lesen, um zu prüfen, ob es Next.js, React oder plain HTML ist.
- Prüfen, ob React und Frontend-Dependencies vorhanden sind.
*Decision Driver*: Falls Next.js genutzt wird, MUSS in Next.js `output: 'export'` konfiguriert werden, da Capacitor nur mit einem statischen HTML/CSS/JS-Build (typischerweise im `out`-Ordner) funktioniert. Für React (Vite/CRA) entsprechend den `build` oder `dist` Ordner nutzen.

E) Assumptions & Open Questions
- **Assumptions**: Das Frontend ist höchstwahrscheinlich eine React/Next.js-Anwendung. Der Host-Server läuft unter Linux (daher kann hier nur Code gescaffoldet, aber iOS nicht final kompiliert werden). Der User benötigt am Ende die generierten Ordner lokal.
- **Open Questions**: Hat der User bereits einen Apple Developer Account (für TestFlight, 99$/Jahr) und einen Google Play Console Account (einmalig 25$)? (Default: Wir gehen davon aus, dass der User diese Accounts nun anlegen muss. Die Dokumentation wird das erklären.)

F) Plan by 3-Layer Architecture
*Layer 1 — Directives*
- Es gelten die "Capacitor Mobile Build" Best Practices: Web-Assets werden gebaut (`npm run build`) und durch `npx cap sync` in die vorbereiteten nativen Projekte kopiert. Keine Modifikationen direkt im `ios/` oder `android/` Code ohne expliziten Grund.

*Layer 2 — Orchestration*
- Schritt 1: Frontend analysieren und für statischen Export konfigurieren.
- Schritt 2: Capacitor im Frontend installieren und initialisieren.
- Schritt 3: Android und iOS Plattformen hinzufügen (`npx cap add android`, `npx cap add ios`).
- Schritt 4: `MOBILE_PUBLISHING_GUIDE.md` für den User verfassen. Dieser Guide enthält genau, was der User gefragt hat: "Wie bekomme ich es auf mein Handy zum Testen und wie später in die Stores."

*Layer 3 — Execution*
- `npm install @capacitor/core` und `npm install -D @capacitor/cli` im Frontend-Directory ausführen.
- `npx cap init` ausführen (mit passender App ID, z.B. `com.fakecheck.app`).
- `npm i @capacitor/android @capacitor/ios`.
- `npx cap add android` und `npx cap add ios`.
- Guide für den User in das Hauptverzeichnis schreiben.

G) Concrete Execution Checklist for Claude
1. **Frontend identifizieren**: Navigiere in das Verzeichnis des Frontends (z.B. Storefront oder FakeCheck Frontend). Prüfe `package.json`.
2. **Abhängigkeiten installieren**: Führe `npm install @capacitor/core` und `npm install -D @capacitor/cli` aus.
3. **SSG (Static Site Generation) konfigurieren**:
   - Falls Next.js: `next.config.js` / `next.config.mjs` anpassen. `output: 'export'` hinzufügen. Image-Components auf `unoptimized: true` setzen.
   - Falls lokales Daten-Fetching passiert, sicherstellen, dass Routen statisch exportierbar sind oder Laufzeitfehler abgefangen werden.
4. **Capacitor initialisieren**: Führe `npx cap init "FakeCheck App" "com.fakecheck.app" --web-dir out` aus (oder `dist`/`build` falls kein Next.js).
5. **Plattformen hinzufügen**: `npm i @capacitor/android @capacitor/ios` installieren. Danach `npx cap add android` und `npx cap add ios` ausführen.
6. **Build & Sync testen**: Führe `npm run build` im Frontend aus und danach `npx cap sync`.
7. **User-Guide schreiben**: Erstelle `/home/serveradmin/Fake Check App/MOBILE_PUBLISHING_GUIDE.md`. Dieser **MUSS** folgende Kapitel für den User enthalten:
   - *Lokales Testen auf dem Android-Handy* (Android Studio installieren, App-Ordner laden, Handy anstecken, "Play" drücken).
   - *Lokales Testen auf dem iPhone* (Mac & Xcode benötigt, Ordner `ios` öffnen, Apple ID hinterlegen, auf lokalem iPhone ausführen).
   - *Veröffentlichen im Google Play Store & Internal Testing* (Account erstellen, AAB Bundle in Android Studio bauen, Internal Test Track hochladen).
   - *Veröffentlichen im Apple App Store & TestFlight* (Apple Developer Program beitreten, in Xcode "Archive" erstellen, zu App Store Connect hochladen, TestFlight einrichten).

H) Troubleshooting
- **Missing `out` / `dist` directory**: Wenn Capacitor den Fehler wirft, dass der web-dir Pfad nicht existiert, sicherstellen, dass `npm run build` fehlerfrei durchlief und die Next-Config `output: 'export'` enthält.
- **Image Error in Next.js Build**: Falls der static Export abbricht wegen `next/image` ohne konfigurierten Loader, zwingend in `next.config.js` für Images `unoptimized: true` setzen.
- **Puffer/Memory Issues**: Falls NPM oder Build hängen bleiben, Server RAM checken. Eventuell NODE_OPTIONS=--max-old-space-size=2048 verwenden.

I) Rollback Plan
- Wenn die Capacitor-Integration das bestehende Projekt kaputt macht: Lösche die Verzeichnisse `android/` und `ios/` sowie `capacitor.config.json` per `rm -rf`.
- Entferne die installierten Packages mit `npm uninstall @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android`.
- Setze die `next.config.js` auf ihren ursprünglichen Zustand via `git restore next.config.mjs` (oder manuell) zurück.

J) Definition of Done
- Capacitor Packages sind installiert.
- Native `android` und `ios` Ordner existieren.
- Web-Basis lässt sich erfolgreich bauen (`npm run build`) und synchronisieren (`npx cap sync`).
- Ein dedizierter, leicht verständlicher `MOBILE_PUBLISHING_GUIDE.md` für den User liegt im Workspace bereit.

K) Activation & Final Functional Test
- Gehe in das Frontend-Verzeichnis.
- Führe `npm run build` aus.
- Führe `npx cap sync` aus.
- Prüfe ob der Ordner `android/app/src/main/assets/public/` existiert und die index.html enthält (`ls -la android/app/src/main/assets/public/`).
- Überprüfe, dass `MOBILE_PUBLISHING_GUIDE.md` existiert und gut gegliedert ist.

L) Sources
- Capacitor Documentation (https://capacitorjs.com/docs)
- Next.js Static HTML Export (https://nextjs.org/docs/pages/building-your-application/deploying/static-exports)

# Caddy & URL Reliability Rules
1. **Never Overwrite**: Never replace the Caddyfile with a new file from memory. Always read the current active Caddyfile first (`/home/serveradmin/LuiInventions/server_setup/caddy_config/Caddyfile`) and use precise edits (`replace_file_content`).
2. **Backup First**: Before any edit, create a timestamped backup: `cp Caddyfile Caddyfile.bak.$(date +%Y%m%d_%H%M%S)`.
3. **Validate Before Reload**: Always run `caddy validate --config <path_to_caddyfile>` before applying changes. If it fails, fix the syntax immediately.
4. **Verify Upstream**: Before proxying to a port (e.g., :3000), verify the service is listening using `ss -tlnp | grep :3000` or `docker ps`.
5. **Connectivity Gate**: After every change, perform a local smoke test: `curl -I -k --resolve your-domain.com:443:127.0.0.1 https://your-domain.com`. Only report "Success" if the URL returns the expected status code.
6. **Preserve Global Blocks**: Ensure the global options block (e.g., email for SSL) remains intact at the top of the file.
