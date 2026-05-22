# Bot RealDebrid

Un bot de Telegram para subir torrents y convertir enlaces compatibles en enlaces directos usando la API de RealDebrid.

## Características

- Procesa archivos `.torrent` enviados por el superusuario.
- Sube torrents a RealDebrid automáticamente.
- Detecta URLs en mensajes de texto y las convierte en enlaces directos si son compatibles.
- Solo responde al usuario definido en la variable `SUPER_USER`.
- Envía notificaciones de inicio y cierre del bot.

## Requisitos

- Python 3.10+ (o versión compatible con `asyncio` y `telebot` async)
- Librerías Python:
  - `pyTelegramBotAPI`
  - `python-dotenv`
  - `rdapi`

## Instalación

1. Clona o descarga el repositorio.
2. Crea un entorno virtual (recomendado):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instala las dependencias:
   ```powershell
   pip install pyTelegramBotAPI python-dotenv rdapi
   ```

## Configuración

Crea un archivo `.env` en la misma carpeta con estas variables:

```env
TELEGRAM_TOKEN=tu_token_de_telegram
SUPER_USER=id_del_superusuario
```

- `TELEGRAM_TOKEN`: Token del bot de Telegram.
- `SUPER_USER`: ID numérico del usuario autorizado a usar el bot.

## Uso

1. Ejecuta el bot:
   ```powershell
   python .\bot_realdebrid.py
   ```
2. En Telegram, envía un archivo `.torrent` al bot o comparte un enlace en un mensaje.
3. El bot responderá con el enlace directo generado por RealDebrid o con mensajes de error.

## Comandos

- `/fin` - Detiene el bot (solo el superusuario puede usarlo).

## Notas

- El bot está diseñado para uso privado con un solo usuario autorizado.
- Asegúrate de que el archivo `.torrent` se envíe como documento y no como texto.
- La funcionalidad de envío de enlaces directos depende de que RealDebrid soporte el enlace.
