# Mobile Publishing Guide: FakeCheck App 📱

Dieser Leitfaden erklärt dir Schritt für Schritt, wie du die von Claude Code generierten iOS- und Android-App-Ordner auf deinem eigenen PC öffnest, die App auf deinem Smartphone testest und später in die App-Stores bringst.

---

## 🚀 Teil 1: Vorbereitungen (Dein PC/Mac)

Da der Server die Apps nur in "Code" generieren kann, musst du die App auf deinem eigenen Rechner kompilieren (bauen). 
1. Lade dir die App-Dateien (den im Plan genannten `android` und `ios` Ordner) von deinem Server auf deinen PC herunter (z. B. via SFTP / FileZilla / VS Code).
2. Installiere **Node.js**: [nodejs.org](https://nodejs.org/) (falls nicht vorhanden).
3. Für **Android**: Installiere [Android Studio](https://developer.android.com/studio).
4. Für **iOS**: Du **musst** einen Mac haben. Installiere **Xcode** aus dem Mac App Store.

---

## 🤖 Teil 2: Testen auf dem Android-Handy

### 1. In Android Studio öffnen
1. Öffne Android Studio.
2. Klicke auf **"Open"** und wähle den heruntergeladenen `android`-Ordner aus.
3. Warte, bis Gradle die Einrichtung abgeschlossen hat (Ladebalken unten rechts fertig).

### 2. Handy vorbereiten
1. Gehe in den Einstellungen deines Handys auf "Über das Telefon".
2. Tippe 7-mal schnell auf "Build-Nummer", bis du Entwickler bist.
3. Gehe in die "Entwickleroptionen" und aktiviere **USB-Debugging**.
4. Schließe dein Handy per USB-Kabel an deinen PC an und erlaube den Zugriff.

### 3. App starten
1. Oben in Android Studio sollte nun dein Handy-Modell neben dem grünen "Play"-Button (Run) auftauchen.
2. Klicke auf den **grünen Play-Button**. Die App wird installiert und öffnet sich auf deinem Handy! 🎉

---

## 🍏 Teil 3: Testen auf dem iPhone (Mac erforderlich!)

### 1. In Xcode öffnen
1. Öffne den heruntergeladenen `ios/App`-Ordner.
2. Mache einen Doppelklick auf die Datei `App.xcworkspace`. Xcode öffnet sich.

### 2. Apple ID hinterlegen
1. Gehe in Xcode in der Menüleiste auf `Xcode > Settings > Accounts`.
2. Füge über das kleine `+` unten links deine Apple ID hinzu.
3. Klicke links in der Dateibaum-Ansicht ganz oben auf **App**. Gehe in den Reiter **Signing & Capabilities**.
4. Wähle bei "Team" deinen Namen (Personal Team) aus.

### 3. Handy anschließen & starten
1. Schließe dein iPhone per USB an den Mac an ("Diesem Computer vertrauen").
2. Gehe an deinem iPhone zu *Einstellungen > Datenschutz & Sicherheit*. Ganz unten: **Entwicklermodus aktivieren** (iPhone startet neu).
3. Wähle oben in Xcode dein iPhone aus der Geräteliste aus.
4. Klicke auf den großen **Play-Button** (Run) oben links.

*(Tipp: Beim ersten Mal musst du u. U. auf deinem iPhone in den Einstellungen > Allgemein > VPN & Geräteverwaltung dem Entwickler-Zertifikat vertrauen).*

---

## 🚀 Teil 4: Veröffentlichen im Google Play Store

Wenn du bereit für den Launch (oder breitem Testing) bist:

1. **Google Play Console Account:** Erstelle einen Account auf der [Google Play Console](https://play.google.com/console/about/) (kostet einmalig $25).
2. **Bundle erstellen:** In Android Studio gehst du oben auf `Build > Generate Signed Bundle / APK...`. Wähle **Android App Bundle (.aab)** aus, erstelle einen Key Store (gut merken/sichern!) und klicke auf Finish.
3. **Internal Testing (Testzugang für andere):** 
   - Gehe in die Google Play Console und erstelle eine neue App.
   - Gehe links auf **Tests > Interne Tests**.
   - Lade deine `.aab`-Datei hoch. Füge die Gmail-Adressen deiner Tester hinzu. Diese können die App nun über einen Link sicher testen.
4. **Veröffentlichung:** Wenn alles passt, kannst du das Release in "Produktion" überführen, die Store-Texte ausfüllen und zur Überprüfung durch Google einreichen.

---

## 🍏 Teil 5: Veröffentlichen im Apple App Store (TestFlight)

1. **Apple Developer Program:** Ein "Personal Team" reicht hierfür nicht mehr. Du musst dich beim [Apple Developer Program](https://developer.apple.com/programs/) anmelden ($99/Jahr).
2. **Archiv erstellen:** 
   - Wähle in Xcode oben als Gerät "Any iOS Device (arm64)" aus.
   - Klicke im Menü auf `Product > Archive`. (Hierfür musst du mit deinem Entwickler-Account in "Signing & Capabilities" das echte Team auswählen).
3. **Zu App Store Connect hochladen:** Wenn das Archive fertig ist, öffnet sich der Organizer. Klicke rechts auf **Distribute App** und folge den Anweisungen bis zum Upload.
4. **TestFlight (Testzugang für andere):**
   - Gehe auf [App Store Connect](https://appstoreconnect.apple.com/).
   - Wähle deine App (oder lege sie an).
   - Gehe auf den Reiter **TestFlight**.
   - Nach etwas Verarbeitungszeit kannst du Tester per E-Mail einladen oder einen öffentlichen Testlink generieren. Die Nutzer brauchen nur die [TestFlight-App](https://apps.apple.com/de/app/testflight/id899247664).
5. **Veröffentlichung:** Reiche die App aus App Store Connect heraus zum Review bei Apple ein. Nach Genehmigung ist sie im Store!
