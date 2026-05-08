"""
Popula coordenadas e porte populacional dos municipios brasileiros.
Execucao: python manage.py popular_coords_municipios

Fontes:
  - kelvins/municipios-brasileiros CSV  → lat/lng + flag capital
  - IBGE Estimativas Populacionais 2021 → populacao para classificar porte
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

IBGE_POP_URL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021"
    "/variaveis/9324?localidades=N6[all]"
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
    help = "Popula coordenadas e porte populacional dos municipios"

    def handle(self, *args, **options):
        # ── 1. Coordenadas + flag capital (kelvins CSV) ──────────
        self.stdout.write("Baixando coordenadas (kelvins CSV)...")
        resp = requests.get(CSV_URL, timeout=30)
        resp.raise_for_status()

        coords = {}
        for row in csv.DictReader(io.StringIO(resp.text)):
            code = str(row.get("codigo_ibge", "")).strip()
            if not code or len(code) < 7:
                continue
            try:
                lat = float(row["latitude"])
                lng = float(row["longitude"])
            except (ValueError, KeyError):
                continue
            uf      = UF_POR_PREFIXO.get(int(code[:2]), "")
            capital = str(row.get("capital", "0")).strip() == "1"
            coords[code] = {
                "lat": lat, "lng": lng, "uf": uf,
                "nome": row.get("nome", "").strip(),
                "capital": capital,
                "porte": "Capital" if capital else "",
            }

        self.stdout.write(f"  {len(coords)} municipios carregados.")

        # ── 2. Populacao IBGE 2021 → classifica porte ───────────
        self.stdout.write("Baixando estimativas populacionais IBGE 2021...")
        try:
            resp_pop = requests.get(IBGE_POP_URL, timeout=60)
            resp_pop.raise_for_status()
            data_pop = resp_pop.json()
            series   = data_pop[0]["resultados"][0]["series"]
            acertos  = 0
            for item in series:
                code    = item["localidade"]["id"]
                pop_str = list(item["serie"].values())[0]
                try:
                    pop = int(str(pop_str).replace(".", "").replace(",", "").strip() or 0)
                except ValueError:
                    pop = 0
                if code in coords and not coords[code]["capital"]:
                    coords[code]["porte"] = "Acima de 80mil" if pop >= 80000 else "Abaixo de 80mil"
                    acertos += 1
            self.stdout.write(f"  {acertos} municipios classificados por populacao.")
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"  Aviso: nao foi possivel baixar populacao IBGE ({e}). "
                "Apenas capitais terao porte definido."
            ))

        # ── 3. Salva ──────────────────────────────────────────────
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(coords, f, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(
            f"Concluido! {len(coords)} municipios salvos."
        ))
