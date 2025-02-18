import os
import pandas as pd
from yt_dlp import YoutubeDL

# Nombre del archivo Excel
excel_file = "videos.xlsx" # Estructura (URL || Estado || Nombre)

# Leer el archivo Excel
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
else:
    print("No se encontró el archivo Excel.")
    exit()

# Crear carpeta de descargas si no existe
download_folder = "descargas_mp3"
os.makedirs(download_folder, exist_ok=True)

# Configuración de yt-dlp
ydl_opts = {
    'format': 'bestaudio',  # Descargar solo el mejor audio disponible
    'postprocessors': [{  
        'key': 'FFmpegExtractAudio',  
        'preferredcodec': 'mp3',  # Convertir el audio a MP3
        'preferredquality': '192',  # Calidad del audio (puedes cambiarlo a 320 si quieres)
    }],
    'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
}

# Descargar solo los videos que tienen estado "Falta"
with YoutubeDL(ydl_opts) as ydl:
    for index, row in df.iterrows():
        url = row['URL']
        estado = row.get('Estado', 'Falta')  # Si no hay estado, asumir "Falta"

        if estado == "Descargado":
            print(f"Saltando (ya descargado): {url}")
            continue

        print(f"Descargando: {url}")
        try:
            info = ydl.extract_info(url, download=True)  # Extrae info del video
            video_title = info.get('title', 'Desconocido')  # Obtiene el título
            print(f"Descargado: {video_title}")  # Muestra el título en la consola

            df.at[index, 'Estado'] = "Descargado"
            df.at[index, 'Nombre'] = video_title  # Guarda el nombre en el Excel
        except Exception as e:
            print(f"Error al descargar {url}: {e}")


# Guardar el Excel actualizado
df.to_excel(excel_file, index=False)
print("Proceso finalizado. Archivo actualizado.")