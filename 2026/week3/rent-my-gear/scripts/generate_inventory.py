#!/usr/bin/env python3
"""
Inventory Generator Script

Generates 50 mock equipment items with real Unsplash images.
Uses the Unsplash API to fetch image URLs based on item names.

Usage:
    uv run generate_inventory.py

Requirements:
    - UNSPLASH_ACCESS_KEY in .env file
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from parent directory
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Output path for inventory JSON
OUTPUT_PATH = PROJECT_ROOT / "src" / "data" / "inventory.json"


# Define 50 items across 3 categories
ITEMS = [
    # Fotografía y Video (17 items)
    {
        "name": "Canon EOS R5",
        "category": "fotografia-video",
        "description": "Cámara mirrorless full-frame profesional con grabación 8K",
        "specs": {"sensor": "45MP Full-Frame", "video": "8K RAW", "estabilización": "IBIS 8 stops"},
        "dailyRate": 150,
        "searchTerm": "canon camera professional",
    },
    {
        "name": "Sony A7 IV",
        "category": "fotografia-video",
        "description": "Cámara mirrorless híbrida para foto y video",
        "specs": {"sensor": "33MP Full-Frame", "video": "4K 60fps", "autofocus": "759 puntos"},
        "dailyRate": 120,
        "searchTerm": "sony mirrorless camera",
    },
    {
        "name": "DJI Ronin RS3 Pro",
        "category": "fotografia-video",
        "description": "Estabilizador gimbal profesional para cámaras cinema",
        "specs": {"carga": "4.5kg", "autonomía": "12h", "transmisión": "LiDAR"},
        "dailyRate": 75,
        "searchTerm": "camera gimbal stabilizer",
    },
    {
        "name": "Sony FX6",
        "category": "fotografia-video",
        "description": "Cámara de cine compacta full-frame",
        "specs": {"sensor": "10.2MP Full-Frame", "video": "4K 120fps", "ISO": "hasta 409600"},
        "dailyRate": 250,
        "searchTerm": "cinema camera professional",
    },
    {
        "name": "Aputure 600d Pro",
        "category": "fotografia-video",
        "description": "Luz LED daylight profesional para cine",
        "specs": {"potencia": "600W", "temperatura": "5600K", "CRI": "96+"},
        "dailyRate": 85,
        "searchTerm": "studio light professional",
    },
    {
        "name": "Canon RF 70-200mm f/2.8L",
        "category": "fotografia-video",
        "description": "Teleobjetivo zoom profesional para RF mount",
        "specs": {"apertura": "f/2.8", "estabilización": "5 stops", "peso": "1070g"},
        "dailyRate": 65,
        "searchTerm": "telephoto lens camera",
    },
    {
        "name": "DJI Mavic 3 Cine",
        "category": "fotografia-video",
        "description": "Drone profesional con cámara Hasselblad",
        "specs": {"sensor": "4/3 CMOS", "video": "5.1K", "vuelo": "46 min"},
        "dailyRate": 180,
        "searchTerm": "professional drone aerial",
    },
    {
        "name": "Sennheiser MKH 416",
        "category": "fotografia-video",
        "description": "Micrófono shotgun de referencia para cine",
        "specs": {"patrón": "Super-cardioide", "respuesta": "40Hz-20kHz", "ruido": "13dB-A"},
        "dailyRate": 45,
        "searchTerm": "shotgun microphone professional",
    },
    {
        "name": "Blackmagic URSA Mini Pro 12K",
        "category": "fotografia-video",
        "description": "Cámara de cine digital 12K con Super 35",
        "specs": {"resolución": "12K", "sensor": "Super 35", "dinámica": "14 stops"},
        "dailyRate": 350,
        "searchTerm": "blackmagic cinema camera",
    },
    {
        "name": "Godox AD600 Pro",
        "category": "fotografia-video",
        "description": "Flash estroboscópico portátil de alta potencia",
        "specs": {"potencia": "600Ws", "TTL": "Sí", "HSS": "1/8000s"},
        "dailyRate": 55,
        "searchTerm": "flash strobe photography",
    },
    {
        "name": "Atomos Ninja V+",
        "category": "fotografia-video",
        "description": "Monitor grabador 5\" con ProRes RAW",
        "specs": {"pantalla": "5.2\" HDR", "grabación": "8K ProRes RAW", "brillo": "1000 nits"},
        "dailyRate": 70,
        "searchTerm": "video monitor recorder",
    },
    {
        "name": "Sigma 24-70mm f/2.8 DG DN Art",
        "category": "fotografia-video",
        "description": "Zoom estándar premium para mirrorless",
        "specs": {"apertura": "f/2.8", "construcción": "19 elementos", "peso": "830g"},
        "dailyRate": 50,
        "searchTerm": "camera lens zoom",
    },
    {
        "name": "Profoto B10X Plus",
        "category": "fotografia-video",
        "description": "Flash de estudio portátil premium",
        "specs": {"potencia": "500Ws", "TTL": "Sí", "autonomía": "400 disparos"},
        "dailyRate": 90,
        "searchTerm": "studio flash profoto",
    },
    {
        "name": "Zhiyun Crane 4",
        "category": "fotografia-video",
        "description": "Gimbal compacto para cámaras mirrorless",
        "specs": {"carga": "6kg", "autonomía": "14h", "pantalla": "OLED táctil"},
        "dailyRate": 60,
        "searchTerm": "gimbal stabilizer video",
    },
    {
        "name": "Rode NTG5",
        "category": "fotografia-video",
        "description": "Micrófono shotgun broadcast ligero",
        "specs": {"patrón": "Supercardioide", "peso": "76g", "respuesta": "20Hz-20kHz"},
        "dailyRate": 40,
        "searchTerm": "microphone recording boom",
    },
    {
        "name": "SmallRig Video Kit",
        "category": "fotografia-video",
        "description": "Kit de jaula y accesorios para video",
        "specs": {"compatibilidad": "Universal", "material": "Aluminio", "peso": "450g"},
        "dailyRate": 25,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Tilta Nucleus-M",
        "category": "fotografia-video",
        "description": "Sistema de follow focus inalámbrico",
        "specs": {"alcance": "100m", "motores": "2", "batería": "8h"},
        "dailyRate": 95,
        "searchTerm": None,  # No image - AI fallback
    },
    # Montaña y Camping (17 items)
    {
        "name": "Tienda MSR Hubba Hubba NX 2",
        "category": "montana-camping",
        "description": "Tienda ultraligera 2 personas para trekking",
        "specs": {"peso": "1.54kg", "capacidad": "2 personas", "estaciones": "3"},
        "dailyRate": 35,
        "searchTerm": "camping tent mountain",
    },
    {
        "name": "Saco Thermarest Hyperion 20",
        "category": "montana-camping",
        "description": "Saco de dormir ultraligero con plumón 900FP",
        "specs": {"temperatura": "-6°C", "peso": "680g", "relleno": "Plumón 900FP"},
        "dailyRate": 28,
        "searchTerm": "sleeping bag hiking",
    },
    {
        "name": "Mochila Osprey Atmos AG 65",
        "category": "montana-camping",
        "description": "Mochila de trekking con sistema AntiGravity",
        "specs": {"capacidad": "65L", "peso": "2.18kg", "espalda": "AntiGravity"},
        "dailyRate": 22,
        "searchTerm": "hiking backpack osprey",
    },
    {
        "name": "Bastones Black Diamond Alpine Carbon Cork",
        "category": "montana-camping",
        "description": "Bastones de trekking ultraligeros de carbono",
        "specs": {"material": "Carbono", "peso": "490g/par", "ajuste": "FlickLock Pro"},
        "dailyRate": 12,
        "searchTerm": "trekking poles hiking",
    },
    {
        "name": "Hornillo MSR WindBurner",
        "category": "montana-camping",
        "description": "Sistema de cocina integrado a prueba de viento",
        "specs": {"potencia": "7000BTU", "tiempo": "4.5min/1L", "peso": "432g"},
        "dailyRate": 15,
        "searchTerm": "camping stove cooking",
    },
    {
        "name": "Colchoneta Sea to Summit Ether Light XT",
        "category": "montana-camping",
        "description": "Colchoneta inflable ultraligera con R-Value 3.2",
        "specs": {"R-Value": "3.2", "peso": "425g", "grosor": "10cm"},
        "dailyRate": 18,
        "searchTerm": "sleeping pad camping",
    },
    {
        "name": "Linterna Petzl NAO RL",
        "category": "montana-camping",
        "description": "Linterna frontal reactiva de alto rendimiento",
        "specs": {"lúmenes": "1500", "autonomía": "15h", "peso": "145g"},
        "dailyRate": 10,
        "searchTerm": "headlamp hiking night",
    },
    {
        "name": "Filtro Katadyn BeFree 1L",
        "category": "montana-camping",
        "description": "Filtro de agua ultraligero para trekking",
        "specs": {"capacidad": "1L", "flujo": "2L/min", "peso": "59g"},
        "dailyRate": 8,
        "searchTerm": "water filter camping",
    },
    {
        "name": "Crampones Petzl Irvis Hybrid",
        "category": "montana-camping",
        "description": "Crampones técnicos para alpinismo",
        "specs": {"puntas": "10", "fijación": "Hybrid", "peso": "725g/par"},
        "dailyRate": 20,
        "searchTerm": "crampons mountaineering ice",
    },
    {
        "name": "Piolet Petzl Summit Evo",
        "category": "montana-camping",
        "description": "Piolet técnico para alpinismo clásico",
        "specs": {"longitud": "59cm", "peso": "315g", "material": "Acero/Aluminio"},
        "dailyRate": 15,
        "searchTerm": "ice axe mountaineering",
    },
    {
        "name": "GPS Garmin inReach Mini 2",
        "category": "montana-camping",
        "description": "Comunicador satelital con GPS y SOS",
        "specs": {"conectividad": "Satélite Iridium", "autonomía": "14 días", "peso": "100g"},
        "dailyRate": 25,
        "searchTerm": "gps satellite hiking",
    },
    {
        "name": "Arnés Petzl Sitta",
        "category": "montana-camping",
        "description": "Arnés ultraligero para escalada y alpinismo",
        "specs": {"peso": "270g", "tipo": "Regulable", "certificación": "CE EN 12277"},
        "dailyRate": 12,
        "searchTerm": "climbing harness rock",
    },
    {
        "name": "Cuerda Beal Joker 9.1mm 60m",
        "category": "montana-camping",
        "description": "Cuerda dinámica unicore para escalada deportiva",
        "specs": {"diámetro": "9.1mm", "longitud": "60m", "peso": "54g/m"},
        "dailyRate": 18,
        "searchTerm": "climbing rope dynamic",
    },
    {
        "name": "Casco Petzl Meteor",
        "category": "montana-camping",
        "description": "Casco híbrido ligero para escalada y alpinismo",
        "specs": {"peso": "240g", "certificación": "CE EN 12492", "ventilación": "Sí"},
        "dailyRate": 10,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Tienda Hilleberg Nallo 2 GT",
        "category": "montana-camping",
        "description": "Tienda 4 estaciones para condiciones extremas",
        "specs": {"peso": "2.4kg", "capacidad": "2 personas", "estaciones": "4"},
        "dailyRate": 55,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Mochila Hyperlite Mountain Gear 3400",
        "category": "montana-camping",
        "description": "Mochila ultraligera de Dyneema",
        "specs": {"capacidad": "55L", "peso": "879g", "material": "Dyneema"},
        "dailyRate": 30,
        "searchTerm": "ultralight backpack hiking",
    },
    {
        "name": "Kit de Cocina Snow Peak Trek 900",
        "category": "montana-camping",
        "description": "Set de cocina compacto de titanio",
        "specs": {"material": "Titanio", "capacidad": "900ml", "peso": "175g"},
        "dailyRate": 14,
        "searchTerm": "camping cookware titanium",
    },
    # Deportes Acuáticos (16 items)
    {
        "name": "Tabla SUP Red Paddle Voyager 12'6\"",
        "category": "deportes-acuaticos",
        "description": "Paddle board inflable touring premium",
        "specs": {"longitud": "12'6\"", "capacidad": "150kg", "peso": "11.5kg"},
        "dailyRate": 45,
        "searchTerm": "paddle board sup water",
    },
    {
        "name": "Kayak Hobie Mirage Compass",
        "category": "deportes-acuaticos",
        "description": "Kayak con sistema de pedales MirageDrive",
        "specs": {"longitud": "12'", "capacidad": "180kg", "propulsión": "MirageDrive GT"},
        "dailyRate": 85,
        "searchTerm": "kayak fishing sport",
    },
    {
        "name": "Traje Seco Kokatat Gore-Tex",
        "category": "deportes-acuaticos",
        "description": "Traje seco profesional para kayak y rafting",
        "specs": {"material": "Gore-Tex Pro", "sellado": "Triple", "látex": "Cuello y puños"},
        "dailyRate": 55,
        "searchTerm": "dry suit kayak water",
    },
    {
        "name": "Remo Werner Cyprus",
        "category": "deportes-acuaticos",
        "description": "Remo de kayak touring de fibra de carbono",
        "specs": {"material": "Carbono", "peso": "680g", "palas": "Ajustables"},
        "dailyRate": 18,
        "searchTerm": "kayak paddle carbon",
    },
    {
        "name": "Chaleco Salvavidas Astral YTV",
        "category": "deportes-acuaticos",
        "description": "PFD de alto rendimiento para kayak y SUP",
        "specs": {"flotabilidad": "70N", "peso": "450g", "bolsillos": "2 frontales"},
        "dailyRate": 12,
        "searchTerm": "life jacket kayak water",
    },
    {
        "name": "Wetsuit O'Neill Psycho Tech 5/4mm",
        "category": "deportes-acuaticos",
        "description": "Traje de neopreno premium para aguas frías",
        "specs": {"grosor": "5/4mm", "material": "TechnoButter 3", "costuras": "Selladas"},
        "dailyRate": 35,
        "searchTerm": "wetsuit surfing diving",
    },
    {
        "name": "Tabla Surf Firewire Dominator 2",
        "category": "deportes-acuaticos",
        "description": "Tabla híbrida para surf de alto rendimiento",
        "specs": {"construcción": "Linear Flex Technology", "quillas": "Futures", "volumen": "35.9L"},
        "dailyRate": 40,
        "searchTerm": "surfboard wave sport",
    },
    {
        "name": "Equipo Buceo Mares Quantum",
        "category": "deportes-acuaticos",
        "description": "Kit completo BCD + regulador para buceo",
        "specs": {"BCD": "Quantum", "regulador": "Dual ADJ", "profundidad": "50m"},
        "dailyRate": 75,
        "searchTerm": "scuba diving equipment",
    },
    {
        "name": "Máscara Buceo Cressi Big Eyes Evolution",
        "category": "deportes-acuaticos",
        "description": "Máscara de buceo con visión panorámica",
        "specs": {"volumen": "Bajo", "cristales": "Templado", "silicona": "Premium"},
        "dailyRate": 10,
        "searchTerm": "diving mask underwater",
    },
    {
        "name": "Aletas Mares Avanti Quattro Power",
        "category": "deportes-acuaticos",
        "description": "Aletas de buceo de alto rendimiento",
        "specs": {"material": "Bimaterial", "propulsión": "Canal", "tallas": "Regular/XL"},
        "dailyRate": 12,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Ordenador Buceo Shearwater Peregrine",
        "category": "deportes-acuaticos",
        "description": "Computadora de buceo recreativo avanzada",
        "specs": {"pantalla": "AMOLED 2.2\"", "algoritmo": "Buhlmann ZHL-16c", "recargable": "Sí"},
        "dailyRate": 35,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Tabla Windsurf Starboard iQFoil",
        "category": "deportes-acuaticos",
        "description": "Tabla olímpica de foil windsurf",
        "specs": {"longitud": "95L", "foil": "Carbono", "uso": "Racing"},
        "dailyRate": 120,
        "searchTerm": "windsurfing board water",
    },
    {
        "name": "Vela Windsurf Severne Turbo GT",
        "category": "deportes-acuaticos",
        "description": "Vela freerace de alto rendimiento",
        "specs": {"tamaño": "7.8m²", "cambers": "3", "material": "Monofilm X-Ply"},
        "dailyRate": 45,
        "searchTerm": "windsurfing sail sport",
    },
    {
        "name": "Cometa Kitesurf Duotone Rebel",
        "category": "deportes-acuaticos",
        "description": "Cometa freeride-wave versátil",
        "specs": {"tamaño": "10m²", "tipo": "C-Shape híbrida", "barra": "Trust Bar"},
        "dailyRate": 65,
        "searchTerm": "kitesurfing kite beach",
    },
    {
        "name": "Tabla Kitesurf Core Fusion 5",
        "category": "deportes-acuaticos",
        "description": "Twin-tip freeride versátil",
        "specs": {"longitud": "140cm", "construcción": "Carbono Wood", "fijaciones": "Ajustables"},
        "dailyRate": 35,
        "searchTerm": None,  # No image - AI fallback
    },
    {
        "name": "Arnés Kite ION Apex Curv 13",
        "category": "deportes-acuaticos",
        "description": "Arnés de cintura premium para kitesurf",
        "specs": {"construcción": "Curv Tech", "cierre": "Spectre Bar", "peso": "1.2kg"},
        "dailyRate": 22,
        "searchTerm": None,  # No image - AI fallback
    },
]


def fetch_unsplash_image(search_term: str) -> str | None:
    """
    Fetch the first image URL from Unsplash for a given search term.
    Returns the regular size image URL or None if not found.
    """
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY not set, skipping image fetch")
        return None

    try:
        response = requests.get(
            UNSPLASH_API_URL,
            params={
                "query": search_term,
                "per_page": 1,
                "orientation": "landscape",
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            return data["results"][0]["urls"]["regular"]

        return None

    except requests.RequestException as e:
        print(f"⚠️  Failed to fetch image for '{search_term}': {e}")
        return None


def generate_inventory():
    """
    Generate the inventory JSON file with Unsplash images.
    """
    print("🔧 Generating inventory...")
    print(f"📍 Output: {OUTPUT_PATH}")
    print()

    if not UNSPLASH_ACCESS_KEY:
        print("❌ UNSPLASH_ACCESS_KEY is required!")
        print("   Please add it to your .env.local file")
        sys.exit(1)

    inventory = []
    items_with_images = 0
    items_without_images = 0

    for idx, item in enumerate(ITEMS, start=1):
        item_data = {
            "id": f"gear-{idx:03d}",
            "name": item["name"],
            "category": item["category"],
            "description": item["description"],
            "specs": item["specs"],
            "dailyRate": item["dailyRate"],
            "imageURL": None,
        }

        search_term = item.get("searchTerm")

        if search_term:
            print(f"[{idx:02d}/50] Fetching image for: {item['name']}...")
            image_url = fetch_unsplash_image(search_term)

            if image_url:
                item_data["imageURL"] = image_url
                items_with_images += 1
                print(f"       ✅ Image found")
            else:
                items_without_images += 1
                print(f"       ⚠️  No image found")

            # Rate limiting - Unsplash allows 50 requests per hour for demo apps
            time.sleep(0.5)
        else:
            items_without_images += 1
            print(f"[{idx:02d}/50] {item['name']} - No image (AI fallback)")

        inventory.append(item_data)

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write inventory to JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print(f"✅ Inventory generated successfully!")
    print(f"   📦 Total items: {len(inventory)}")
    print(f"   🖼️  Items with images: {items_with_images}")
    print(f"   🤖 Items for AI fallback: {items_without_images}")
    print(f"   📁 Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_inventory()
