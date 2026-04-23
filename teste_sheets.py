import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Escopos necessários
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Caminho para o arquivo JSON
creds_path = ".secrets/fnp-radar-sheets.json"

# Autenticação
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# ID da planilha principal do projeto
# Pegue o ID da URL da planilha:
# https://docs.google.com/spreadsheets/d/  <<ID AQUI>>  /edit
SHEET_ID = "1L5uuiTqoz9aDUAVflGww1UnZfp7xFntcmvoB_jeS3Og"

# Abre a planilha
planilha = client.open_by_key(SHEET_ID)

# Lista as abas disponíveis
abas = [sheet.title for sheet in planilha.worksheets()]
print("Abas encontradas:", abas)

# Testa leitura da aba Governança
aba = planilha.worksheet("Governança")
dados = aba.get_all_values()
print(f"Linhas lidas: {len(dados)}")
print("Primeiras 3 linhas:")
for linha in dados[:3]:
    print(linha)