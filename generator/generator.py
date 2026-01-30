import os
import json
from PIL import Image, ImageFont, ImageColor, ImageDraw

# Fingerprint-Bildgenerator importieren
from .fingerprint import build_masked_fingerprint_image

# Globale Farbpalette laden
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
palette_path = os.path.join(base_dir, "assets", "color_palettes", "palette.json")

with open(palette_path, encoding="utf-8") as f:
    palette = json.load(f)

# Basis-Asset-Pfade korrekt auflösen
fonts_dir = os.path.join(base_dir, "assets", "fonts")
prof_pictures_dir = os.path.join(base_dir, "assets", "prof_pictures")
backgrounds_dir = os.path.join(base_dir, "assets", "backgrounds_fingerprint")
def parse_color(val):
    """
    Wandelt eine Farbangabe in ein RGB-Tupel um.
    - val: entweder hex "#RRGGBB", ein Palette-Schlüssel oder ein RGB-Tupel/Liste
    """
    if not val:
        # Default schwarz, falls kein Wert
        return tuple(palette.get("black", [0,0,0]))
    if isinstance(val, str):
        if val.startswith("#"):
            return ImageColor.getrgb(val)
        return tuple(palette.get(val, [255, 255, 255]))
    # Annahme: Liste/Tupel
    return tuple(val)

def fit_text(draw, text, font_path, initial_size, max_width, max_height, min_size=10, step=2, spacing=4):
    """Bricht Text um und passt Schriftgröße an."""
    size = initial_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        lines = []
        line = ""
        # build wrapped lines with word-splitting for very long words
        for word in text.split():
            # if word itself too wide, split into character chunks
            bbox_word = draw.textbbox((0,0), word, font=font)
            if bbox_word[2] > max_width:
                part = ""
                for ch in word:
                    test = part + ch
                    if draw.textbbox((0,0), test, font=font)[2] <= max_width:
                        part = test
                    else:
                        if line:
                            lines.append(line)
                            line = ""
                        lines.append(part)
                        part = ch
                if part:
                    if line:
                        line += " " + part
                    else:
                        line = part
                continue
            # normal wrap at spaces
            test_line = (line + " " if line else "") + word
            bbox_test = draw.textbbox((0,0), test_line, font=font)
            if bbox_test[2] <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        # Gesamt-Höhe der Zeilen berechnen
        total_h = sum(
            draw.textbbox((0,0), ln, font=font)[3] - draw.textbbox((0,0), ln, font=font)[1]
            for ln in lines
        ) + spacing * (len(lines)-1)
        if total_h <= max_height:
            return font, "\n".join(lines)
        size -= step
    # fallback: kleinste Schriftgröße, kein Umbruch
    return ImageFont.truetype(font_path, min_size), text

def wrap_text(draw, text, font, max_width, hyphenator=None, hyphen="-"):
    """Umbricht Text an Wortgrenzen und trennt lange Wörter mit Hyphenation."""
    # Vorab: Falls Hyphenation aktiv, zerlege lange Wörter in Silben
    raw_words = text.split()
    words = []
    for word in raw_words:
        if hyphenator and draw.textbbox((0,0), word, font=font)[2] > max_width:
            # Höchstens einmal trennen: nimm letzte mögliche Silbengrenze
            positions = hyphenator.positions(word)
            split_pos = None
            for pos in reversed(positions):
                part = word[:pos] + hyphen
                if draw.textbbox((0,0), part, font=font)[2] <= max_width:
                    split_pos = pos
                    break
            if split_pos:
                words.append(word[:split_pos] + hyphen)
                words.append(word[split_pos:])
            else:
                words.append(word)
        else:
            words.append(word)

    lines = []
    current = ""
    for w in words:
        test_line = (current + " " if current else "") + w
        if draw.textbbox((0,0), test_line, font=font)[2] <= max_width:
            current = test_line
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def draw_centered_text(draw, rect, text, font, fill):
    """Zeichnet Einzeiler zentriert in Rechteck."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = x0 + (w - text_w) / 2
    text_y = y0 + (h - text_h) / 2
    draw.text((text_x, text_y), text, fill=fill, font=font)

def draw_centered_multiline_text(draw, rect, text, font, fill, align="left", spacing=4):
    """Zeichnet mehrzeiligen Text zentriert in Rechteck."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align=align)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = x0 + (w - text_w) / 2
    text_y = y0 + (h - text_h) / 2
    draw.multiline_text((text_x, text_y), text, fill=fill, font=font, spacing=spacing, align=align)

def place_professor(canvas, prof_image, target_center, head_width):
    """Skaliert und platziert Dozentenbild zentriert."""
    # Proportional skalieren
    w, h = prof_image.size
    scale = head_width / w
    new_size = (int(w * scale), int(h * scale))
    prof_resized = prof_image.resize(new_size, Image.LANCZOS)

    # Position berechnen (Mittelpunkt)
    paste_x = int(target_center[0] - new_size[0] / 2)
    paste_y = int(target_center[1] - new_size[1] / 2)

    # als RGBA einfügen
    canvas.alpha_composite(prof_resized, dest=(paste_x, paste_y))
    return paste_x, paste_y, new_size[0], new_size[1]

# ===== Hilfsfunktion: Dynamische Box mit Text =====
def draw_text_box(draw, x0, x1, y_ref, text, font, box_fill, outline, radius, padding, line_spacing, text_fill, show_box=True, hyphenator=None, hyphen="-", align_y="center", offset_x=0, offset_y=0):
    """
    Zeichnet eine gerundete Box um den mehrzeiligen Text und schreibt den Text zentriert hinein.
    x0, x1: horizontale Slice-Grenzen
    y_center: vertikaler Mittelpunkt der Box
    text: String (bereits ggf. mit wrap_text aufgeteilt)
    font: PIL-Font
    fill, outline, radius, padding, line_spacing: Box-Styling
    """
    # Bei leerem Text nichts zeichnen
    if not text or not text.strip():
        return None
    # Wortumbruch
    max_w = x1 - x0 - 2 * padding
    lines = wrap_text(draw, text, font, max_w, hyphenator, hyphen)
    # Zeilenmaße
    heights = [draw.textbbox((0,0), ln, font=font)[3] - draw.textbbox((0,0), ln, font=font)[1] for ln in lines]
    widths  = [draw.textbbox((0,0), ln, font=font)[2] - draw.textbbox((0,0), ln, font=font)[0] for ln in lines]
    total_h = sum(heights) + line_spacing * (len(lines)-1)
    box_h   = total_h + 2 * padding
    box_w   = (max(widths) if widths else 0) + 2 * padding
    # Kein Zeichnen, wenn Box zu klein erscheint (verhindert einzelne Pixel/Punkte)
    if box_w <= padding*2 and box_h <= padding*2:
        return None
    # Box-POS
    box_x0 = int(x0 + ( (x1-x0) - box_w) / 2)
    if align_y == "center":
        box_y0 = int(y_ref - box_h/2)
    else:  # "top"
        box_y0 = int(y_ref)
    # Offset für per-Slice-Versatz
    box_x0 += offset_x
    box_y0 += offset_y
    box_x1 = box_x0 + box_w
    box_y1 = box_y0 + box_h
    # Debug-Ausgabe vor Box-Zeichnung
    # Box zeichnen
    if show_box:
        draw.rounded_rectangle(
            [(box_x0, box_y0), (box_x1, box_y1)],
            radius=radius,
            fill=box_fill,
            outline=outline,
            width=4
        )
    # Text zeichnen mit konsistenter Zeilenhöhe
    # Vorberechnung: bboxes und Zeilenhöhen
    bboxes = [draw.textbbox((0, 0), ln, font=font) for ln in lines]
    heights = [b[3] - b[1] for b in bboxes]
    widths = [b[2] - b[0] for b in bboxes]
    if heights:
        max_h = max(heights)
        # Korrektur für y-Start basierend auf kleinstem bbox[1]
        min_y = min(b[1] for b in bboxes)
        offset = padding - min_y
    else:
        max_h = 0
        offset = padding

    for idx, ln in enumerate(lines):
        bbox = bboxes[idx]
        text_w = widths[idx]
        # Horizontale Zentrierung
        tx = box_x0 + (box_w - text_w) / 2
        # Vertikale Position mit konsistenter Zeilenhöhe
        ty = box_y0 + offset
        draw.text((tx, ty), ln, fill=text_fill, font=font)
        # Zeilen-Offset aktualisieren
        offset += max_h + line_spacing
    return (box_x0, box_y0, box_x1, box_y1)

# === Hauptfunktion ===

def create_socialmedia_carousel(config):
    # Modul-Konfiguration extrahieren
    if 'modules' in config and isinstance(config['modules'], list) and config['modules']:
        module_config = config['modules'][0]
    else:
        module_config = config
    # Falls Module selbst nochmals in module_config geschachtelt sind, entpacken
    if isinstance(module_config, dict) and 'modules' in module_config and isinstance(module_config['modules'], list) and module_config['modules']:
        module_config = module_config['modules'][0]

    module_id = module_config.get('id', module_config.get('title', 'unknown'))

    # Display-Flags aus Modul-Config
    disp = module_config.get("display", {})
    show_title_box     = disp.get("title_box", config.get("slice1_title_box_enabled", False))
    show_info1_box     = disp.get("info_box",   config.get("slice1_box_enabled",    False))
    show_semester_box  = disp.get("semester_box",config.get("slice1_semester_box_enabled", True))
    show_lecturer_box  = disp.get("lecturer_box",config.get("slice2_box_enabled",    True))
    show_info3_box     = disp.get("footer_box",  config.get("slice3_box_enabled",    True))

    # Offsets aus Modul-Config
    offs = module_config.get("offsets", {})
    off1 = offs.get("slice1", {})
    t_off_x, t_off_y = off1.get("title", [0,0])
    i1_off_x, i1_off_y = off1.get("info",  [0,0])
    sem_off_x, sem_off_y = off1.get("semester", [0,0])
    off2 = offs.get("slice2", {})
    lect_off_x, lect_off_y = off2.get("lecturer", [0, 0])
    off3 = offs.get("slice3", {})
    i3_off_x, i3_off_y = off3.get("info", [0,0])
    # 1) Canvas erstellen
    width, height = config.get("output_size", [3240, 1350])
    base_w, base_h = 3240, 1350
    scale_w = width / base_w
    scale_h = height / base_h
    scale = min(scale_w, scale_h)
    slices = config.get("slice_count", 3)
    full = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # 2) Hintergrund setzen

    # Hintergrundfarbe ermitteln: bevorzugt aus Modul-Config, sonst aus Hauptconfig
    mod_bg_cfg = module_config.get("background", {})
    if isinstance(mod_bg_cfg, dict) and mod_bg_cfg.get("type") == "palette":
        bg_color_key = mod_bg_cfg.get("value")
    else:
        bg = config.get("background", {})
        bg_color_key = bg.get("value")
    palette_overrides = module_config.get("palette_overrides") or {}
    box_color_keys  = palette_overrides.get("boxes", module_config.get("box_colors", {}))
    module_text_colors = module_config.get("text_colors", {})
    text_color_keys = palette_overrides.get("text", module_text_colors)
    # Standard-Textfarbe aus Palette
    default_text_color = tuple(palette.get("black", [0,0,0]))
    def get_text_color(key):
        color_key = text_color_keys.get(key)
        if not color_key:
            return default_text_color
        return parse_color(color_key)

    # === ursprünglicher Farb-Background entfernt ===

    # === neuer Hintergrund: Fingerprint-Bild als Hintergrundbild ===
    draw = ImageDraw.Draw(full)  # Zeichenobjekt wird dennoch gebraucht
    fingerprint_config = module_config.get("fingerprint")
    if fingerprint_config and fingerprint_config.get("enabled", False):
        try:
            fp_img = build_masked_fingerprint_image(fingerprint_config)
            fp_mode = fingerprint_config.get("background_mode", "inset")  # "inset" oder "centered"

            if fp_mode == "centered":
                from PIL import ImageOps
                fp_resized = ImageOps.contain(fp_img, (width, height))
                fp_w, fp_h = fp_resized.size
                paste_x = (width - fp_w) // 2
                paste_y = (height - fp_h) // 2
                col = parse_color(bg_color_key)
                draw.rectangle([(0, 0), (width, height)], fill=col)
                fp_alpha = fp_resized.copy()
                fp_alpha_val = fingerprint_config.get("background_alpha", 200)
                fp_alpha.putalpha(fp_alpha_val)
                full.paste(fp_alpha, (paste_x, paste_y), fp_alpha)

            # Fingerprint-Bild unten links mit optionaler Skalierung einfügen
            elif fp_mode == "inset":
                from PIL import ImageOps
                col = parse_color(bg_color_key)
                draw.rectangle([(0, 0), (width, height)], fill=col)
                max_fp_width  = fingerprint_config.get("fingerprint_max_width", width // 3)
                max_fp_height = fingerprint_config.get("fingerprint_max_height", height // 2)
                fp_scaled = ImageOps.contain(fp_img, (max_fp_width, max_fp_height))
                pos_x = fingerprint_config.get("fingerprint_offset_x", 50)
                pos_y = fingerprint_config.get("fingerprint_offset_y", height - fp_scaled.height - 50)
                full.paste(fp_scaled, (pos_x, pos_y), fp_scaled)

            else:
                print(f"[WARN] Unbekannter background_mode '{fp_mode}', fallback auf 'inset'")
                col = parse_color(bg_color_key)
                draw.rectangle([(0, 0), (width, height)], fill=col)
                pos_x = fingerprint_config.get("fingerprint_offset_x", 50)
                pos_y = fingerprint_config.get("fingerprint_offset_y", height - fp_img.height - 50)
                full.paste(fp_img, (pos_x, pos_y), fp_img)

        except Exception as e:
            print(f"[WARN] Fingerprint-Hintergrund konnte nicht geladen werden: {e}")
    else:
        # Fingerprint ist deaktiviert – trotzdem Hintergrundfarbe ausfüllen!
        col = parse_color(bg_color_key)
        draw.rectangle([(0, 0), (width, height)], fill=col)

    # Hyphenation optional konfigurieren
    hyphenation_config = config.get("hyphenation", {})
    hyphenator = None
    if hyphenation_config.get("enabled", False):
        import pyphen
        lang = hyphenation_config.get("lang", "de_DE")
        hyphen = hyphenation_config.get("hyphen", "-")
        hyphenator = pyphen.Pyphen(lang=lang)

    # 3) Schriftarten laden (Modul-Config)
    font_config = module_config.get("fonts", {})
    def load_font(key, default_path, default_size):
        spec = font_config.get(key, {})
        size = spec.get("size", default_size)
        font_path = spec.get("path", default_path)
        if not os.path.isabs(font_path):
            font_path = os.path.join(fonts_dir, os.path.basename(font_path))
        return ImageFont.truetype(font_path, int(size * scale))
    try:
        font_title    = load_font("title",    config.get("title_font_path", "assets/fonts/Roboto-Bold.ttf"), config.get("title_font_size", 80))
        font_slice1   = load_font("slice1_info", config.get("slice1_info_font_path", "assets/fonts/Roboto-Regular.ttf"), config.get("slice1_info_font_size", 48))
        font_semester = load_font("semester", config.get("semester_font_path", "assets/fonts/Roboto-Bold.ttf"), config.get("semester_font_size", 60))
        font_lecturer = load_font("lecturer", config.get("lecturer_font_path", "assets/fonts/Roboto-Regular.ttf"), config.get("lecturer_font_size", 48))
        font_slice3   = load_font("slice3_info", config.get("slice3_info_font_path", "assets/fonts/Roboto-Regular.ttf"), config.get("slice3_info_font_size", 48))
    except:
        font_title = font_slice1 = font_semester = font_lecturer = font_slice3 = ImageFont.load_default()

    # Spacings aus Modul-Config
    spacings = module_config.get("spacings", {})
    sp1 = spacings.get("slice1", {})
    title_ls = int(sp1.get("title", {}).get("line_spacing", 10) * scale)
    title_pad= int(sp1.get("title", {}).get("padding",      0) * scale)
    info_ls  = int(sp1.get("info",  {}).get("line_spacing", 10) * scale)
    info_pad = int(sp1.get("info",  {}).get("padding",      50) * scale)
    sem_marg = spacings.get("semester", {}).get("margin", [50, 50])
    sp3 = spacings.get("slice3", {})
    info3_ls  = int(sp3.get("info", {}).get("line_spacing", config.get("slice3_line_spacing", 10)) * scale)
    box3_yoff = sp3.get("box_y_offset", config.get("slice3_box_y_offset", 0))
    box3_yoff = int(box3_yoff * scale)

    # 4) Modul-Bilder einfügen
    # (Entfernt: bottom_image-Block zur Vermeidung kleiner Icons/Punkte)

    # Dozentenbild: flexibel fithten und positionieren
    # Modul-spezifische Lecturer-Einstellungen
    lect_cfg = module_config.get("lecturer", {})
    photo_path = lect_cfg.get("photo")
    if photo_path and not os.path.isabs(photo_path):
        photo_path = os.path.join(prof_pictures_dir, os.path.basename(photo_path))
    if photo_path and not os.path.exists(photo_path):
        pass
    if photo_path and os.path.exists(photo_path):
        target_w    = int(lect_cfg.get("target_width", 400) * scale)
        target_h    = int(lect_cfg.get("target_height", 400) * scale)
        # Pfad wird aus lect_cfg["photo"] geladen
        prof_img = Image.open(photo_path).convert("RGBA")
        w, h = prof_img.size
        # Always use "contain" mode
        ratio = min(target_w / w, target_h / h)
        new_size = (int(w * ratio), int(h * ratio))
        resized = prof_img.resize(new_size, Image.LANCZOS)
        # Dozentenbild rechteckig und ohne Maske einfügen
        # Dozentenbild rechteckig mit transparentem Hintergrund einfügen
        canvas_img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        paste_pos = ((target_w - new_size[0]) // 2, (target_h - new_size[1]) // 2)
        canvas_img.paste(resized, paste_pos, resized)
        # Zielposition unten im 2. Slice
        slice_w = width // slices
        offset_x = int(lect_cfg.get("offset_x", 0) * scale)
        offset_y = int(lect_cfg.get("offset_y", 0) * scale)
        base_x = slice_w + (slice_w - target_w)//2 + offset_x
        base_y = height - target_h + offset_y
        full.paste(canvas_img, (int(base_x), int(base_y)), canvas_img)



    # 5) Textboxen zeichnen
    slice_w = width // slices
    padding = int(50 * scale)
    radius = int(config.get("box_radius", 20) * scale)
    # Farben für Boxen
    def get_box_color(key, fallback):
        val = box_color_keys.get(key)
        if val is not None:
            return parse_color(val)
        return fallback
    # Defaults für Boxfarben
    box_fill_default = tuple(palette.get("secondary", [255, 255, 255]))
    box_outline = tuple(palette.get("text_dark", [0, 0, 0]))
    slice1_fill = get_box_color("slice1", box_fill_default)
    slice2_fill = get_box_color("slice2", box_fill_default)
    slice3_fill = get_box_color("slice3", palette.get("highlight", box_fill_default))

    # 1. Slice: Titel
    title = module_config.get("title") or module_config.get("id", "")
    x0, x1 = 0, slice_w
    y0 = padding * 2
    t_off_x, t_off_y = [int(t_off_x * scale), int(t_off_y * scale)]
    draw_text_box(
        draw, x0, x1, y0,
        title, font_title,
        slice1_fill, box_outline, radius,
        title_pad, title_ls,
        get_text_color("title"),
        show_box=show_title_box,
        hyphenator=hyphenator,
        hyphen=hyphenation_config.get("hyphen", "-"),
        align_y="top",
        offset_x=t_off_x,
        offset_y=t_off_y
    )

    # 1. Slice: Info
    if module_config.get("slice1_info"):
        info1 = module_config.get("slice1_info", "")
        x0, x1 = 0, slice_w
        y_center = padding + (height/2 - padding) * 0.5
        i1_off_x, i1_off_y = [int(i1_off_x * scale), int(i1_off_y * scale)]
        draw_text_box(
            draw, x0, x1, y_center,
            info1, font_slice1,
            slice1_fill, box_outline, radius,
            info_pad, info_ls,
            get_text_color("slice1_info"),
            show_box=show_info1_box,
            hyphenator=hyphenator,
            hyphen=hyphenation_config.get("hyphen", "-"),
            offset_x=i1_off_x,
            offset_y=i1_off_y
        )

    # Semester-Box
    sem = module_config.get("semester", "")
    margin_h, margin_v = sem_marg if isinstance(sem_marg, (list,tuple)) and len(sem_marg)==2 else (padding, padding)
    margin_h = int(margin_h * scale)
    margin_v = int(margin_v * scale)
    sem_off_x, sem_off_y = [int(sem_off_x * scale), int(sem_off_y * scale)]
    bbox_sem = draw.textbbox((0, 0), sem, font=font_semester)
    sem_w = bbox_sem[2] - bbox_sem[0]
    sem_h = bbox_sem[3] - bbox_sem[1]
    box_w = sem_w + 2 * margin_h
    box_h = sem_h + 2 * margin_v
    box_x0 = int((slice_w - box_w) / 2)
    box_y0 = int(height / 2 - box_h / 2)
    box_x0 += sem_off_x
    box_y0 += sem_off_y
    box_x1 = box_x0 + box_w
    box_y1 = box_y0 + box_h
    if show_semester_box:
        draw.rounded_rectangle(
            [(box_x0, box_y0), (box_x1, box_y1)],
            radius=radius,
            fill=slice1_fill,
            outline=box_outline,
            width=4
        )
    text_x = box_x0 + margin_h
    bbox_sem = draw.textbbox((0, 0), sem, font=font_semester)
    text_y = box_y0 + margin_v - bbox_sem[1]
    draw.text((text_x, text_y), sem, fill=get_text_color("semester"), font=font_semester)

    # 2. Slice: Dozentenname
    x0, x1 = slice_w, slice_w * 2
    lect_name = module_config.get("lecturer", {}).get("name", "")
    lect_off_x, lect_off_y = [int(lect_off_x * scale), int(lect_off_y * scale)]
    y_center = height / 2 + lect_off_y
    if lect_name:
        draw_text_box(
            draw, x0, x1, y_center,
            lect_name, font_lecturer,
            slice2_fill, box_outline, radius,
            padding, info_ls,
            get_text_color("slice2_info"),
            show_box=show_lecturer_box,
            hyphenator=hyphenator,
            hyphen=hyphenation_config.get("hyphen", "-"),
            offset_x=lect_off_x
        )

    # 3. Slice: Modulinfo
    if module_config.get("slice3_info"):
        info3 = module_config.get("slice3_info", "")
        x0, x1 = slice_w * 2, slice_w * 3
        i3_off_x, i3_off_y = [int(i3_off_x * scale), int(i3_off_y * scale)]
        y_center = height / 2 + box3_yoff
        draw_text_box(
            draw, x0, x1, y_center,
            info3, font_slice3,
            slice3_fill, box_outline, radius,
            padding, info3_ls,
            get_text_color("slice3_info"),
            show_box=show_info3_box,
            hyphenator=hyphenator,
            hyphen=hyphenation_config.get("hyphen", "-"),
            offset_x=i3_off_x,
            offset_y=i3_off_y
        )

    # Optional: Fingerprint-Bild einfügen, falls konfiguriert (entfernt: alte Methode)

    # 6) Bilder speichern
    output_dir = config.get("output_path", "output")
    os.makedirs(output_dir, exist_ok=True)
    full.convert("RGB").save(os.path.join(output_dir, "post.png"))
    print(f"✅ Full image saved: {os.path.join(output_dir, 'post.png')}")

    for i in range(slices):
        box = (i * slice_w, 0, (i + 1) * slice_w, height)
        part = full.crop(box).convert("RGB")
        out_p = os.path.join(output_dir, f"post_{i+1}.png")
        part.save(out_p)
        print(f"✅ Slice {i+1} gespeichert: {out_p}")