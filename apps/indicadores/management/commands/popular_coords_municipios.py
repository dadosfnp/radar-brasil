"""
Popula coordenadas de todos os municipios brasileiros.
Execucao: python manage.py popular_coords_municipios

Usa o dataset kelvins/municipios-brasileiros (CSV unico, ~5570 municipios, < 5s).
"""
import csv
import io
import json
import os
import requests
from django.core.management.base import BaseCommand

OUTPUT = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "municipios_coords.json"
)

CSV_URL = (
    "https://raw.githubusercontent.com/kelvins/municipios-brasileiros"
    "/main/csv/municipios.csv"
)

UF_POR_PREFIXO = {
    11:"RO", 12:"AC", 13:"AM", 14:"RR", 15:"PA", 16:"AP", 17:"TO",
    21:"MA", 22:"PI", 23:"CE", 24:"RN", 25:"PB", 26:"PE", 27:"AL",
    28:"SE", 29:"BA",
    31:"MG", 32:"ES", 33:"RJ", 35:"SP",
    41:"PR", 42:"SC", 43:"RS",
    50:"MS", 51:"MT", 52:"GO", 53:"DF",
}


class Command(BaseCommand):
    help = "Popula coordenadas dos municipios (kelvins/municipios-brasileiros CSV)"

    def handle(self, *args, **options):
        self.stdout.write(f"Baixando CSV de {CSV_URL} ...")
        resp = requests.get(CSV_URL, timeout=30)
        resp.raise_for_status()

        reader = csv.DictReader(io.StringIO(resp.text))
        coords = {}
        for row in reader:
            code = str(row.get("codigo_ibge", "")).strip()
            if not code or len(code) < 7:
                continue
            try:
                lat  = float(row["latitude"])
                lng  = float(row["longitude"])
            except (ValueError, KeyError):
                continue
            uf   = UF_POR_PREFIXO.get(int(code[:2]), "")
            nome = row.get("nome", "").strip()
            coords[code] = {"lat": lat, "lng": lng, "uf": uf, "nome": nome}

        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(coords, f, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(
            f"Concluido! {len(coords)} municipios salvos em {OUTPUT}"
        ))
