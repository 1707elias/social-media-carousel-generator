import json
import random
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw

DEFAULT_SIDES: List[str] = ["top", "right", "bottom", "left"]


def load_config(path: str) -> dict:
    """
    Lädt die JSON-Konfiguration von dem angegebenen Pfad.
    Setzt erforderlichen Basis-Wert ("base_size"), der automatisch
    zone_thickness, grid.rect_width und grid.rect_height setzt.
    """
    with open(path, 'r') as f:
        config = json.load(f)

    # Base size must be provided to set all core dimensions
    if "base_size" not in config:
        raise KeyError("Configuration must include 'base_size'")
    base = config["base_size"]
    # Override zone thickness and grid dimensions
    config["zone_thickness"] = base
    grid = config.get("grid", {})
    grid["rect_width"] = base
    grid["rect_height"] = base
    config["grid"] = grid

    return config


def create_zone_mask(img_width: int, img_height: int, zone_thickness: int, zone_count: int = 3, enabled_sides: Optional[List[str]] = None) -> Image.Image:
    """
    Erstellt eine Graustufen-Maske mit weißen Bereichen in drei Zonen am Bildrand:
    oben, rechts, unten und links, jeweils mit der gegebenen zone_thickness.
    """
    if enabled_sides is None:
        enabled_sides = DEFAULT_SIDES.copy()
    mask = Image.new("L", (img_width, img_height), 0)
    draw = ImageDraw.Draw(mask)
    for zone in range(zone_count):
        start = zone * zone_thickness
        end = start + zone_thickness
        # Obere Zone
        if "top" in enabled_sides:
            draw.rectangle([0, start, img_width, end], fill=255)
        # Untere Zone
        if "bottom" in enabled_sides:
            draw.rectangle([0, img_height - end, img_width, img_height - start], fill=255)
        # Linke Zone
        if "left" in enabled_sides:
            draw.rectangle([start, 0, end, img_height], fill=255)
        # Rechte Zone
        if "right" in enabled_sides:
            draw.rectangle([img_width - end, 0, img_width - start, img_height], fill=255)
    return mask


def generate_cutout_mask(
    img_width: int,
    img_height: int,
    zone_thickness: int,
    min_rect_width: int,
    max_rect_width: int,
    min_rect_height: int,
    max_rect_height: int,
    count: int,
    zone_count: int = 3,
    enabled_sides: Optional[List[str]] = None,
    overlap: bool = True
) -> Image.Image:
    """
    Erzeugt eine Maske, in der innerhalb des Randbereichs (Zone_count Zonen mit zone_thickness)
    zufällige Aussparungs-Rechtecke (Maskenpixel=0) sind. Die Position wird entlang eines
    kontinuierlichen Ring-Pfads um das Bild gewählt, sodass Rechtecke auch über Ecken gehen können.
    Die Größe der Rechtecke wird zufällig zwischen min/max Breite und Höhe gewählt.
    """
    if enabled_sides is None:
        enabled_sides = DEFAULT_SIDES.copy()
    # Basis-Zonenmaske (weiß in den erlaubten Zonen)
    mask = create_zone_mask(img_width, img_height, zone_thickness, zone_count, enabled_sides)

    draw = ImageDraw.Draw(mask)
    # Ring-Mittel-Linie (halbe Gesamtdicke)
    ring_mid = zone_thickness * zone_count / 2.0
    # Gesamtlänge des Ring-Pfads (Umfang)
    perimeter = 2 * (img_width + img_height)

    for _ in range(count):
        # Zufälliger Punkt auf dem Ring
        t = random.random() * perimeter
        # Bestimme (cx, cy) entlang der Ring-Mittel-Linie
        if t < img_width:
            # Oberseite
            cx = t
            cy = ring_mid
        elif t < img_width + img_height:
            # Rechte Seite
            cx = img_width - ring_mid
            cy = t - img_width
        elif t < 2 * img_width + img_height:
            # Unterseite (rückwärts)
            cx = img_width - (t - (img_width + img_height))
            cy = img_height - ring_mid
        else:
            # Linke Seite (rückwärts)
            cx = ring_mid
            cy = img_height - (t - (2 * img_width + img_height))

        # Zufällige Größe des Rechtecks wählen
        rect_width = random.randint(min_rect_width, max_rect_width)
        rect_height = random.randint(min_rect_height, max_rect_height)

        # Linke obere Ecke des Rechtecks berechnen
        x0 = int(round(cx - rect_width / 2.0))
        y0 = int(round(cy - rect_height / 2.0))
        # Innerhalb des Bildes begrenzen
        x0 = max(0, min(img_width - rect_width, x0))
        y0 = max(0, min(img_height - rect_height, y0))

        # Rechteck in Maske als schwarz (Aussparung) malen
        draw.rectangle([x0, y0, x0 + rect_width, y0 + rect_height], fill=0)

    return mask


def create_grid_cutout_mask(
    img_width: int,
    img_height: int,
    zone_thickness: int,
    rect_w: int,
    rect_h: int,
    omit_chance: float,
    zone_count: int = 3,
    enabled_sides: Optional[List[str]] = None
) -> Image.Image:
    """
    Erstellt eine Cut-Out-Maske mit einem Raster in jeder Zone.
    Zellengröße = rect_w × rect_h, omit_chance = Wahrscheinlichkeit, eine Zelle zu überspringen.
    Anzahl der Reihen/Spalten wird automatisch nach Zonengröße berechnet.
    """
    if enabled_sides is None:
        enabled_sides = DEFAULT_SIDES.copy()

    # Basis-Zonenmaske (weiß in den erlaubten Zonen)
    mask = create_zone_mask(img_width, img_height, zone_thickness, zone_count, enabled_sides)
    draw = ImageDraw.Draw(mask)

    # Definition der Zonen-Rechtecke für jede Seite
    sides = {
        "top":    lambda start: (0, start, img_width, zone_thickness),
        "bottom": lambda start: (0, img_height - (start + zone_thickness), img_width, zone_thickness),
        "left":   lambda start: (start, 0, zone_thickness, img_height),
        "right":  lambda start: (img_width - (start + zone_thickness), 0, zone_thickness, img_height)
    }

    for zone in range(zone_count):
        start = zone * zone_thickness
        for side in enabled_sides:
            x0_zone, y0_zone, zone_w, zone_h = sides[side](start)

            # dynamische Anzahl Reihen und Spalten berechnen
            rows = zone_h // rect_h
            cols = zone_w // rect_w

            for r in range(rows):
                y = y0_zone + r * rect_h
                if y + rect_h > y0_zone + zone_h:
                    break
                for c in range(cols):
                    x = x0_zone + c * rect_w
                    if x + rect_w > x0_zone + zone_w:
                        break
                    if omit_chance > 0.0 and random.random() < omit_chance:
                        continue
                    draw.rectangle([x, y, x + rect_w, y + rect_h], fill=0)

    return mask


def apply_overlay(image_path: str, mask: Image.Image, background_color: Tuple[int, int, int, int]) -> Image.Image:
    """
    Wendet ein farbiges Overlay basierend auf der Maske an.
    Maskenpixel=255: Overlay sichtbar, Maskenpixel=0: Originalbild.
    """
    original = Image.open(image_path).convert("RGBA")
    # Hintergrundfarbe als RGBA-Tupel
    bg = tuple(background_color) if len(background_color) == 4 else (*background_color, 255)
    # Erstelle ein durchgehendes Farbbild
    overlay = Image.new("RGBA", original.size, bg)
    # Maske als Alpha-Kanal setzen
    overlay.putalpha(mask.resize(original.size))
    # Overlay auf das Originalbild anwenden
    return Image.alpha_composite(original, overlay)

def build_masked_fingerprint_image(fingerprint_config: dict) -> Image.Image:
    """
    Erzeugt das finale Fingerprint-Bild basierend auf den Konfigurationsdaten.
    Gibt ein RGBA-Bild zurück.
    """
    from .generator import parse_color  # falls nötig für Farbumwandlung

    random_seed = fingerprint_config.get("random_seed")
    if random_seed is not None:
        random.seed(int(random_seed))

    image = Image.open(fingerprint_config["input_image"]).convert("RGBA")
    rect_width = fingerprint_config.get("base_size")
    rect_height = fingerprint_config.get("base_size")
    mask = create_grid_cutout_mask(
        img_width=image.width,
        img_height=image.height,
        zone_thickness=fingerprint_config.get("base_size"),
        rect_w=rect_width,
        rect_h=rect_height,
        omit_chance=fingerprint_config.get("grid", {}).get("omit_chance", 0.3),
        zone_count=fingerprint_config.get("zone_count", 3),
        enabled_sides=fingerprint_config.get("enabled_sides", ["top", "right", "bottom", "left"])
    )
    bg_color = fingerprint_config.get("background_color", [255, 255, 255])
    if len(bg_color) == 3:
        overlay_color = tuple(bg_color) + (255,)
    else:
        overlay_color = tuple(bg_color)
    overlay = Image.new("RGBA", image.size, overlay_color)
    overlay.putalpha(mask)
    final = Image.alpha_composite(image, overlay)

    return final