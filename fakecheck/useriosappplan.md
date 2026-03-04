# iOS App Publishing Guide für die Fake Check App

Hier ist die detaillierte Anleitung, wie du das Next.js Frontend unserer Fake Check App in eine native iOS App umwandelst und auf deinem Mac baust. 
**Wichtig:** Deine Telegram-Bot-Funktionalität bleibt vollständig erhalten, da sie über das Backend läuft und davon nicht berührt wird.

### 1. Voraussetzungen auf deinem Mac

Bevor wir starten, stelle sicher, dass folgende Software auf deinem Mac installiert ist:
- **Node.js (LTS Version)**: Lade es von [nodejs.org](https://nodejs.org/) herunter und installiere es.
- **Xcode**: Über den Mac App Store kostenlos verfügbar (Du brauchst Xcode zwingend, um iOS Apps zu bauen).
- **CocoaPods**: Öffne dein Terminal auf dem Mac und führe `sudo gem install cocoapods` aus.

### 2. Projekt (Frontend) herunterladen

Ich habe das vorbereitete Frontend für dich als Archiv zusammengestellt. Du kannst es direkt hier herunterladen:

**[Download Fake Check iOS Source](https://start.lui-inventions.com/fakecheck-ios-source.tar.gz)**

Lade die Datei `fakecheck-ios-source.tar.gz` herunter und entpacke sie auf deinem Mac durch einen Doppelklick. Öffne danach das Terminal und navigiere in den entpackten `frontend` Ordner.

### 3. Capacitor installieren (Im Terminal deines Macs)

Navigiere in deinem Terminal auf dem Mac in den Ordner `frontend`:

```bash
cd pfad/zu/deinem/frontend
```

Führe danach diese Befehle aus, um die nötigen Pakete zu laden:

```bash
# 1. Normale Abhängigkeiten installieren (falls noch nicht passiert)
npm install

# 2. Capacitor Core und CLI installieren
npm install @capacitor/core
npm install -D @capacitor/cli

# 3. iOS Plattform für Capacitor installieren
npm install @capacitor/ios
```

### 4. Capacitor initialisieren

Initialisiere Capacitor im `frontend` Verzeichnis:

```bash
npx cap init
```
* Wenn du nach dem App-Namen gefragt wirst: Gib z.B. `FakeCheck` ein.
* Wenn du nach der App-ID gefragt wirst: Gib etwas wie `com.fakecheck.app` (eine eindeutige Bundle ID) ein.
* Wenn du nach dem Web-Dir gefragt wirst: Gib **`out`** ein (sehr wichtig für Next.js static exports!).

### 5. API-URL konfigurieren

Die App muss wissen, wo das Backend läuft, da sie auf dem Handy keine relativen URLs (wie `/api/`) verwenden kann.
Erstelle im `frontend` Ordner auf deinem Mac eine Datei namens `.env` (falls nicht vorhanden) und füge deine Backend-URL ein:

```env
NEXT_PUBLIC_API_URL=https://lui-inventions.com
```

### 6. Bauen und Synchronisieren

Nun baust du das Next.js Projekt und verknüpfst es mit iOS:

```bash
# Baut das Next.js Projekt als statische HTML-Seiten im "out" Ordner
npm run build 

# Füge das iOS-Projekt hinzu
npx cap add ios

# Synchronisiere die gerade gebauten Dateien in das iOS Projekt
npx cap sync
```

### 7. App in Xcode öffnen und testen

Der letzte Schritt erfolgt in Xcode. Xcode kompiliert den fertigen Code in eine native iOS-App.

```bash
# Öffnet das Projekt in Xcode
npx cap open ios
```

Sobald Xcode geöffnet ist:
1. Wähle oben ganz in der Mitte ein Ziel-Gerät aus (z.B. iPhone 16 Pro Simulator oder schließe dein echtes iPhone per Kabel/WLAN an).
2. Klicke auf den großen "Play"-Button ▶️ oben links, um die App zu bauen und im Simulator (oder auf dem Gerät) zu starten.

### Sind Änderungen im Code erforderlich?
Ich habe die nötigen Änderungen im Backend (CORS für `capacitor://localhost` erlaubt) und im Frontend (`output: "export"` in `next.config.ts`) bereits umgesetzt. Damit ist *diese* Codebasis offiziell bereitet für Capacitor auf iOS. Telegram und der Agent funktionieren einfach weiter hin wie bisher!
