# Social Media Carousel Generator 🎨

Ein automatisiertes Tool zur Generierung von Instagram-Carousels für Hochschul-Module, entwickelt in Python.

## ℹ️ Hintergrund des Projekts

Dieses Projekt entstand im Rahmen meines Wirtschaftsinformatik-Studiums an der **THWS Würzburg**. Es war ursprünglich Teil eines größeren Semesterprojekts, das aus vier Software-Komponenten bestand.

**Dieses Repository enthält mein eigenständig entwickeltes Modul:** den **Social Media Generator**.
Während andere Teile des Gesamtprojekts für die Datenbeschaffung zuständig waren, war die Aufgabe dieses Moduls, strukturierte JSON-Daten vollautomatisch in visuell ansprechende Marketing-Assets (Bild-Carousels) zu verwandeln.

*Hinweis: Um Datenschutz und Urheberrecht zu wahren, wurde dieses Repository als "Standalone"-Version veröffentlicht. Echte Personendaten und geschützte Hochschul-Logos wurden durch Platzhalter ersetzt.*

## ✨ Features

- **Automatisierte Bildkomposition:** Erstellt basierend auf JSON-Configs komplette 3-teilige Instagram-Carousels (Intro, Dozentenvorstellung, Moduldetails).
- **Fingerprint-Algorithmus:** Ein selbst geschriebener Algorithmus (`fingerprint.py`), der basierend auf Parametern einzigartige, generative Hintergrundmuster erzeugt.
- **Dynamisches Text-Rendering:** Automatische Berechnung von Schriftgrößen, Zeilenumbrüchen und Text-Boxen mittels `Pillow`, damit Texte immer perfekt in das Layout passen.
- **Modulare Architektur:** Das Design ist strikt vom Code getrennt und über JSON-Dateien (`config/`) steuerbar.

## 🛠 Tech Stack

- **Python 3.x**
- **Pillow (PIL):** Für die pixelgenaue Bildmanipulation und das Rendering.
- **Pyphen:** Für korrekte Silbentrennung bei dynamischen deutschen Texten.
- **JSON:** Für die Konfiguration von Modulen und Styles.

## 🚀 Installation & Nutzung

1. **Repository klonen:**
   ```bash
   git clone [https://github.com/1707elias/social-media-carousel-generator.git](https://github.com/1707elias/social-media-carousel-generator.git)
   cd social-media-carousel-generator
   
2. **Virtuelle Umgebung erstellen & Abhängigkeiten installieren::**
   ```bash
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
3. **Generator starten:**
   ```bash
   python main.py 
Das Skript liest die Konfigurationen aus dem Ordner (`config/`) und speichert die fertigen Bilder im Verzeichnis (`/output`).
   
## 📂 Projektstruktur

```text
.
├── assets/               # Ressourcen (Fonts, Platzhalter-Bilder, Paletten)
├── config/               # JSON-Konfigurationen für die Module
├── generator/            # Kern-Logik (Rendering & Fingerprint-Algorithmus)
├── output/               # Verzeichnis für die generierten Bilder (wird automatisch erstellt)
├── .gitignore            # Schließt Cache und Output vom Git-Tracking aus
├── main.py               # Zentraler Einstiegspunkt des Programms
└── requirements.txt      # Liste der benötigten Python-Bibliotheken

Entwickelt von Elias Schlappner | Wirtschaftsinformatik | THWS