# 📌 Pasos para usar tu código con un entorno virtual

## ✅ 1. Crear y activar un entorno virtual
Si el usuario no tiene un entorno virtual, puede crearlo y activarlo:

- Windows (CMD o PowerShell)

    ```sh
    python -m venv venv
    venv\Scripts\activate  # Activa el entorno en Windows
    ```
- Mac/Linux (Terminal)

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # Activa el entorno en Mac/Linux
    ```

## ✅ 2. Instalar las dependencias
Con el entorno virtual activado, instala las dependencias:

```sh
pip install -r requirements.txt
```

## ✅ 3. Ejecutar el script
Ya con todo instalado, el usuario puede ejecutar tu script normalmente:

```sh
cd src
python main.py
```

## 🔥 Extra: Cómo asegurarte de que FFmpeg esté instalado

Si tu código usa yt-dlp para convertir audios a MP3, es recomendable que el usuario instale FFmpeg.

- Windows: Puede descargarlo desde https://ffmpeg.org/download.html y agregarlo a la variable de entorno.
- Linux/macOS:
    ```sh
    sudo apt install ffmpeg  # Debian/Ubuntu  
    brew install ffmpeg  # macOS  
    ```
Con esto, tu código debería ser fácil de compartir y ejecutar en cualquier máquina. 🚀