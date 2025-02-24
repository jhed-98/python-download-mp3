import os
import gspread
import pandas as pd
import asyncio
from yt_dlp import YoutubeDL
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv  # Importar dotenv
from telegram import Bot # Telegram Bot API

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener valores desde .env
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")  # Archivo JSON de credenciales
SHEET_ID = os.getenv("SHEET_ID")  # ID de la hoja de Google Sheets
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1  

# Crear carpeta de descargas si no existe
download_folder = "descargas_mp3"
os.makedirs(download_folder, exist_ok=True)

# Configuración de yt-dlp
ydl_opts = {
    'format': 'bestaudio',
    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
}

async def enviar_audio_telegram_async(file_path):
    bot = Bot(token=TOKEN)
    with open(file_path, "rb") as audio:
        await bot.send_audio(chat_id=CHAT_ID, audio=audio)
    print(f"✅ Audio enviado por Telegram: {file_path}")

def obtener_nombre_mp3(info):
    """Obtiene el nombre del archivo MP3 descargado."""
    if "requested_downloads" in info:
        for item in info["requested_downloads"]:
            filepath = item.get("filepath", "")
            if filepath.endswith(".mp3"):
                return filepath  
    
    archivos_mp3 = [f for f in os.listdir(download_folder) if f.endswith(".mp3")]
    return os.path.join(download_folder, archivos_mp3[-1]) if archivos_mp3 else None

def obtener_datos():
    """Obtiene los datos de Google Sheets como DataFrame."""
    return pd.DataFrame(sheet.get_all_records())

def actualizar_google_sheets(url, estado, nombre=None):
    """Actualiza el estado y nombre del video en Google Sheets."""
    celdas = sheet.findall(url)
    for celda in celdas:
        sheet.update_cell(celda.row, 2, estado)  # Columna 2 es "Estado"
        if nombre:
            sheet.update_cell(celda.row, 3, nombre)  # Columna 3 es "Nombre"

def descargar_video(url):
    """Descarga un video de YouTube y lo convierte a MP3."""
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"📥 Descargando: {url}")
            info = ydl.extract_info(url, download=True)
            mp3_file = obtener_nombre_mp3(info)
            if mp3_file:
                asyncio.run(enviar_audio_telegram_async(mp3_file))
            else:
                print("⚠ No se encontró un archivo MP3.")
            video_title = info.get('title', 'Desconocido')
            actualizar_google_sheets(url, "Descargado", video_title)
            print(f"✅ Descargado: {video_title}")
        except Exception as e:
            print(f"❌ Error al descargar {url}: {e}")

def agregar_url():
    """Permite ingresar una nueva URL y descargar el video."""
    url = input("Ingrese la URL del video: ").strip()
    nombre = input("Ingrese el nombre del video (opcional): ").strip()
    sheet.append_row([url, "Pendiente", nombre])
    print(f"✅ URL agregada con éxito: {url}")
    descargar_video(url)

def actualizar_estado():
    """Permite actualizar el estado de una URL en Google Sheets."""
    df = obtener_datos()
    print(df)
    url = input("Ingrese la URL del video a actualizar: ").strip()
    estado = input("Ingrese el nuevo estado: ").strip()
    actualizar_google_sheets(url, estado)
    print("✅ Estado actualizado con éxito." if sheet.findall(url) else "⚠️ URL no encontrada.")

def descargar_videos_pendientes():
    """Descarga todos los videos pendientes."""
    df = obtener_datos()
    for _, row in df.iterrows():
        if row.get("Estado", "Falta") != "Descargado":
            descargar_video(row['URL'])
    print("📂 Proceso finalizado. Google Sheets actualizado.")

# Menú interactivo
while True:
    print("\nSeleccione una opción:")
    print("1. Ingresar nueva URL")
    print("2. Actualizar estado de un video")
    print("3. Descargar videos pendientes")
    print("4. Salir")
    
    opcion = input("Opción: ").strip()
    if opcion == "1":
        agregar_url()
    elif opcion == "2":
        actualizar_estado()
    elif opcion == "3":
        descargar_videos_pendientes()
    elif opcion == "4":
        print("👋 Saliendo del programa.")
        break
    else:
        print("❌ Opción inválida. Intente nuevamente.")
