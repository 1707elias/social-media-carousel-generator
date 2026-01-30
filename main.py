import os
import json
from generator import generator

# Basisverzeichnis des Socialmedia-Generators
base_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(base_dir, "config")

def load_json_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    # Alle Modul-Konfigurationsdateien
    module_configs = [os.path.join(config_dir, f) for f in os.listdir(config_dir) if f.endswith(".json") and f != "config.json"]

    # Basis-Konfiguration (optional, falls benötigt)
    config_path = "config/config.json"
    if os.path.exists(config_path):
        base_config = load_json_file(config_path)
    else:
        base_config = {}

    for mod_path in module_configs:
        print(f"\n📄 Verarbeite Moduldatei: {mod_path}")
        mod_config = load_json_file(mod_path)

        # Wir gehen davon aus, dass immer genau ein Modul enthalten ist
        module = mod_config["modules"][0]
        module_id = module.get("id", "MODUL")

        module_title = module.get("title", module_id)
        output_dir = os.path.join("output", module_title.lower().replace(" ", "_"))

        # Ausgabepfad vorbereiten
        os.makedirs(output_dir, exist_ok=True)

        # Konfiguration zusammenführen
        full_config = {
            **base_config,
            "modules": [module],
            "output_path": output_dir
        }

        print(f"\n=== [MODUL: {module_title}] Starte Generierung ===")

        fingerprint_cfg = module.get("fingerprint", {})
        if fingerprint_cfg.get("enabled") and isinstance(fingerprint_cfg.get("random_seed"), int):
            print(f"[INFO] Verwendeter random_seed: {fingerprint_cfg['random_seed']}")

        generator.create_socialmedia_carousel(full_config)

if __name__ == "__main__":
    main()