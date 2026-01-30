# README – Konfigurationsoptionen

## Übersicht
Im `config`-Ordner befinden sich:
- **`config.json`**: Hauptkonfiguration, global gültige Einstellungen.
- **`<modul_id>.json`**: Modul-spezifische Konfigurationen, jeweils eine Datei pro Modul.

---

## Hauptkonfiguration (`config.json`)

### Allgemeine Einstellungen

| Option                | Typ                   | Standard       | Beschreibung                                        |
|-----------------------|-----------------------|----------------|-----------------------------------------------------|
| `output_size`         | `[Breite, Höhe]`      | `[3240, 1350]` | Gesamtgröße des Bild-Canvas in Pixeln               |
| `slice_count`         | `int`                 | `3`            | Anzahl der Slices (Teile)                           |
| `background`          | `object`              | –              | Hintergrundtyp und Wert (Palette-Key oder Hex-Code) |
| `background.type`     | `"palette"`/`"image"` | `"palette"`    | Art des Hintergrunds                                |
| `background.value`    | `string`              | `"petrol"`     | Farbpalette-Schlüssel oder Bildpfad                 |
| `output_dir`          | `string`              | `"output"`     | Verzeichnis für die Ausgabebilder                   |
| `hyphenation`         | `object`              | `{}`           | Einstellungen zur Silbentrennung                    |
| `hyphenation.enabled` | `bool`                | `false`        | Silbentrennung nutzen?                              |
| `hyphenation.lang`    | `string`              | `"de_DE"`      | Sprachcode für Hyphenation                          |
| `hyphenation.hyphen`  | `string`              | `"-"`          | Zeichen am Zeilenende                               |

### Globale Schrift-Einstellungen

| Option                  | Typ      | Standard                            | Beschreibung                       |
|-------------------------|----------|-------------------------------------|------------------------------------|
| `default_font_path`     | `string` | `"assets/fonts/Roboto-Regular.ttf"` | Fallback-Pfad für allgemeine Texte |
| `default_font_size`     | `int`    | `68`                                | Fallback-Schriftgröße              |
| `title_font_path`       | `string` | `"assets/fonts/Roboto-Bold.ttf"`    | Font für Titel in Slice 1          |
| `title_font_size`       | `int`    | `100`                               | Schriftgröße Titel                 |
| `slice1_info_font_path` | `string` | `"assets/fonts/Roboto-Regular.ttf"` | Font für Info Slice 1              |
| `slice1_info_font_size` | `int`    | `68`                                | Schriftgröße Info Slice 1          |
| `lecturer_font_path`    | `string` | `"assets/fonts/Roboto-Bold.ttf"`    | Font für Dozentenname (Slice 2)    |
| `lecturer_font_size`    | `int`    | `68`                                | Schriftgröße Dozentenname          |
| `semester_font_path`    | `string` | `"assets/fonts/Roboto-Bold.ttf"`    | Font für Semester-Box              |
| `semester_font_size`    | `int`    | `100`                               | Schriftgröße Semester              |
| `slice3_info_font_path` | `string` | `"assets/fonts/Roboto-Regular.ttf"` | Font für Info Slice 3              |
| `slice3_info_font_size` | `int`    | `68`                                | Schriftgröße Info Slice 3          |

### Box- und Layout-Einstellungen

| Option                          | Typ      | Standard    | Beschreibung                                              |
|---------------------------------|----------|-------------|-----------------------------------------------------------|
| `box_radius`                    | `int`    | `100`       | Eckenradius für alle Boxen                                |
| `slice1_title_box_enabled`      | `bool`   | `false`     | Zeigt Titel-Box in Slice 1                                |
| `slice1_box_enabled`            | `bool`   | `false`     | Zeigt Info-Box in Slice 1                                 |
| `slice1_semester_box_enabled`   | `bool`   | `true`      | Zeigt Semester-Box in Slice 1                             |
| `slice2_box_enabled`            | `bool`   | `true`      | Zeigt Dozenten-Box in Slice 2                             |
| `slice3_box_enabled`            | `bool`   | `true`      | Zeigt Info-Box in Slice 3                                 |
| `slice1_title_line_spacing`     | `int`    | `10`        | Zeilenabstand für Titeltext                               |
| `slice1_title_padding`          | `int`    | `0`         | Padding in der Titel-Box                                  |
| `slice1_title_info_spacing`     | `int`    | `40`        | Abstand zwischen Titel und Info-Box                       |
| `slice1_line_spacing`           | `int`    | `10`        | Zeilenabstand Info-Text in Slice 1                        |
| `slice3_line_spacing`           | `int`    | `10`        | Zeilenabstand Info-Text in Slice 3                        |
| `slice3_box_y_offset`           | `int`    | `100`       | Vertikale Verschiebung der Box in Slice 3                 |
| `offsets.slice1.title`          | `[x,y]`  | `[0,0]`     | Verschiebung der Titel-Box in Slice 1                     |
| `offsets.slice1.info`           | `[x,y]`  | `[0,0]`     | Verschiebung der Info-Box in Slice 1                      |
| `offsets.slice1.semester`       | `[x,y]`  | `[0,0]`     | Verschiebung der Semester-Box in Slice 1                  |
| `offsets.slice2.lecturer`       | `[x,y]`  | `[0,-250]`  | Verschiebung der Dozenten-Box (Standard Y = -250)         |
| `offsets.slice3.info`           | `[x,y]`  | `[0,0]`     | Verschiebung der Info-Box in Slice 3                      |

---

## Modul-Konfiguration (`<modul_id>.json`)

Jede Modul-Datei enthält ein Objekt mit folgenden Feldern:

### Pflichtfelder

| Feld          | Typ      | Beschreibung                             |
|---------------|----------|------------------------------------------|
| `id`          | `string` | Eindeutige Modul-Kennung (z. B. `GI102`) |
| `title`       | `string` | Modulname                                |
| `slice1_info` | `string` | Kurzinformation für Slice 1              |
| `semester`    | `string` | Semesterangabe (z. B. `1. Semester`)     |
| `slice3_info` | `string` | Modulinfo für Slice 3                    |

### Dozenten-Elemente

| Feld                     | Typ      | Beschreibung                                          |
|--------------------------|----------|-------------------------------------------------------|
| `lecturer.name`          | `string` | Name des Dozenten (wird in Slice 2 angezeigt)         |
| `lecturer.photo`         | `string` | Pfad zur Bilddatei (PNG/JPG)                          |
| `lecturer.target_width`  | `int`    | Zielbreite des Rahmens                                |
| `lecturer.target_height` | `int`    | Zielhöhe des Rahmens                                  |
| `lecturer.offset_x`      | `int`    | Horizontale Feinanpassung in Slice 2                  |
| `lecturer.offset_y`      | `int`    | Vertikale Feinanpassung in Slice 2 (Standard: `-250`) |

### Farben und Boxen

| Feld                      | Typ      | Beschreibung                                 |
|---------------------------|----------|----------------------------------------------|
| `box_colors.slice1`       | `string` | Palette-Key für Füllfarbe der Box in Slice 1 |
| `box_colors.slice2`       | `string` | Palette-Key für Füllfarbe der Box in Slice 2 |
| `box_colors.slice3`       | `string` | Palette-Key für Füllfarbe der Box in Slice 3 |
| `text_colors.title`       | `string` | Textfarbe für den Titel                      |
| `text_colors.slice1_info` | `string` | Textfarbe für Info-Text in Slice 1           |
| `text_colors.semester`    | `string` | Textfarbe für den Semester-Text              |
| `text_colors.slice2_info` | `string` | Textfarbe für Dozentenname (Slice 2)         |
| `text_colors.slice3_info` | `string` | Textfarbe für Info-Text in Slice 3           |

### Anzeige-Steuerung

| Feld                    | Typ    | Beschreibung                                                |
|-------------------------|--------|-------------------------------------------------------------|
| `display.title_box`     | `bool` | Überschreibt global `slice1_title_box_enabled`              |
| `display.info_box`      | `bool` | Überschreibt global `slice1_box_enabled`                    |
| `display.semester_box`  | `bool` | Überschreibt global `slice1_semester_box_enabled`           |
| `display.lecturer_box`  | `bool` | Überschreibt global `slice2_box_enabled`                    |
| `display.footer_box`    | `bool` | Überschreibt global `slice3_box_enabled`                    |

### Schrift- und Layout-Overrides

| Abschnitt               | Typ    | Beschreibung                                                                       |
|-------------------------|--------|------------------------------------------------------------------------------------|
| `fonts.<key>`           | Objekt | `{ path, size }` für `title`, `slice1_info`, `semester`, `lecturer`, `slice3_info` |
| `spacings.slice1.title` | Objekt | `{ line_spacing, padding }`                                                        |
| `spacings.slice1.info`  | Objekt | `{ line_spacing, padding }`                                                        |
| `spacings.semester`     | Objekt | `{ margin: [horizontal, vertical] }`                                               |
| `spacings.slice3.info`  | Objekt | `{ line_spacing }`                                                                 |
| `spacings.slice3`       | Objekt | `{ box_y_offset }`                                                                 |

### Fingerprint-Hintergrund

| Feld                                 | Typ       | Beschreibung                                                         |
|--------------------------------------|-----------|----------------------------------------------------------------------|
| `fingerprint.enabled`                | `bool`    | Aktiviert den Fingerprint-Hintergrund                                |
| `fingerprint.background_mode`        | `string`  | `"inset"` oder `"centered"`                                          |
| `fingerprint.input_image`            | `string`  | Pfad zum Bild für den Fingerprint-Hintergrund                        |
| `fingerprint.background_alpha`       | `int`     | Transparenz (0–255)                                                  |
| `fingerprint.fingerprint_max_width`  | `int`     | Maximalbreite (nur bei `"inset"`)                                    |
| `fingerprint.fingerprint_max_height` | `int`     | Maximalhöhe (nur bei `"inset"`)                                      |
| `fingerprint.fingerprint_offset_x`   | `int`     | Horizontale Positionierung des Fingerprint-Bildes                    |
| `fingerprint.fingerprint_offset_y`   | `int`     | Vertikale Positionierung des Fingerprint-Bildes                      |
| `fingerprint.grid.omit_chance`       | `float`   | Wahrscheinlichkeit, dass Teile des Gitters ausgelassen werden        |
| `fingerprint.zone_count`             | `int`     | Anzahl der Zonen                                                     |
| `fingerprint.base_size`              | `int`     | Basisgröße der Maskenstruktur                                        |
| `fingerprint.background_color`       | `[R,G,B]` | Hintergrundfarbe (falls benötigt)                                    |
| `fingerprint.enabled_sides`          | `array`   | Liste der Kanten, die Masken enthalten sollen (`"top"`, `"left"`, …) |

---

### Hinweise
- Alle Offsets (`offset_x` und `offset_y`) können pro Modul überschrieben werden.
- Fingerprint-Hintergrund wird nur eingeblendet, wenn `fingerprint.enabled = true`.