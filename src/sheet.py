import os
import gspread
import pandas as pd
from yt_dlp import YoutubeDL
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv  # Importar dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener valores desde .env
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")  # Archivo JSON de credenciales
SHEET_ID = os.getenv("SHEET_ID")  # ID de la hoja de Google Sheets

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# Acceder a la hoja de cálculo
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

def obtener_datos():
    """Obtiene los datos de Google Sheets como DataFrame."""
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def agregar_url():
    """Permite ingresar una nueva URL, guardarla en Google Sheets, descargarla y actualizar el estado."""
    url = input("Ingrese la URL del video: ").strip()
    nombre = input("Ingrese el nombre del video (opcional): ").strip()

    # Guardar en Google Sheets con estado "Pendiente"
    nueva_fila = [url, "Pendiente", nombre]
    sheet.append_row(nueva_fila)
    print(f"✅ URL agregada con éxito: {url}")

    # Descargar el video inmediatamente
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"📥 Descargando: {url}")
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Desconocido')
            print(f"✅ Descargado: {video_title}")

            # Buscar la fila en Google Sheets y actualizar el estado y el nombre
            celdas = sheet.findall(url)
            for celda in celdas:
                sheet.update_cell(celda.row, 2, "Descargado")  # Columna 2 es "Estado"
                sheet.update_cell(celda.row, 3, video_title)  # Columna 3 es "Nombre"

        except Exception as e:
            print(f"❌ Error al descargar {url}: {e}")

def actualizar_estado():
    """Permite actualizar el estado de una URL en Google Sheets."""
    df = obtener_datos()
    print(df)  # Mostrar los datos actuales

    url = input("Ingrese la URL del video a actualizar: ").strip()
    estado = input("Ingrese el nuevo estado: ").strip()

    # Buscar la fila donde está la URL
    celdas = sheet.findall(url)
    if celdas:
        for celda in celdas:
            sheet.update_cell(celda.row, 2, estado)  # Columna 2 es "Estado"
        print("✅ Estado actualizado con éxito.")
    else:
        print("⚠️ URL no encontrada.")

def descargar_videos():
    """Descarga los videos que tienen estado 'Falta' y actualiza Google Sheets."""
    df = obtener_datos()
    
    with YoutubeDL(ydl_opts) as ydl:
        for index, row in df.iterrows():
            url = row['URL']
            estado = row.get('Estado', 'Falta')

            if estado == "Descargado":
                # print(f"Saltando (ya descargado): {url}")
                continue

            print(f"Descargando: {url}")
            try:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'Desconocido')
                print(f"Descargado: {video_title}")

                # Buscar la fila en Google Sheets y actualizarla
                celdas = sheet.findall(url)
                for celda in celdas:
                    sheet.update_cell(celda.row, 2, "Descargado")  # Actualizar estado
                    sheet.update_cell(celda.row, 3, video_title)  # Actualizar nombre

            except Exception as e:
                print(f"Error al descargar {url}: {e}")

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
        descargar_videos()
    elif opcion == "4":
        print("👋 Saliendo del programa.")
        break
    else:
        print("❌ Opción inválida. Intente nuevamente.")
