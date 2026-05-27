import os, asyncio, re, sys
from rdapi import RD
from dotenv import load_dotenv
from telebot import asyncio_filters
from telebot.types import *
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
import myjdapi

load_dotenv()  # Load environment variables from .env file
telegram_token=os.getenv('TELEGRAM_TOKEN')
superuser=int(os.getenv('SUPER_USER'))

bot = AsyncTeleBot(telegram_token)
RD = RD()
# print(RD.system.time().content)
# print(RD.user.get().json())
log='-log' in sys.argv
jd=myjdapi.Myjdapi()


def enviar_a_jd(links):
    if jd.is_connected()==False:
        jd.connect(os.getenv('JD_USER'),os.getenv('JD_PASSWORD'))
        jd.update_devices()
    devices=jd.list_devices()
    device=jd.get_device(device_id=devices[0]['id'])
    a=device.linkgrabber.add_links([{"autostart" : True, "links" : link, "destinationFolder" : 'RealDebrid'} for link in links])
    print(a)

torrents_en_descarga = []
async def tarea_de_descargas():
    while True:
        for torrent in torrents_en_descarga:
            info=RD.torrents.info(id=torrent['torrent']['id']).json()
            if log:
                print(info)
            if ('status' in info) and (info['status']=='downloaded'):
                torrents_en_descarga.remove(torrent)
                msg=await bot.send_message(superuser, f"✅ Descarga completada: {info['filename']}\nEnlaces:\n" + '\n'.join(info['links']))
                enviar_a_jd(info['links'])
                await bot.edit_message_text(msg.text + "\n✅ Enlaces agregados a JDownloader." , msg.chat.id, msg.message_id)
        await asyncio.sleep(120)  # Esperar 120 segundos antes de verificar nuevamente

# Handle /fin command
@bot.message_handler(commands=['fin'])
async def comando_fin(message):
    if (message.chat.id==superuser):
        exit()

# handle torrent files
@bot.message_handler(func=lambda message: True, content_types=['document'])
async def subir_torrent(message):
    if (message.chat.id!=superuser):
        return
    if message.document.file_name.endswith('.torrent'):
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(message.document.file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        atorrent=RD.torrents.add_file(filepath=message.document.file_name).json()
        RD.torrents.select_files(id=atorrent['id'], files='all')
        info=RD.torrents.info(id=atorrent['id']).json()
        if log:
            print(info)
        if 'status' in info and info['status'] == 'downloaded':
            msg=await bot.send_message(message.chat.id, f"Archivo {info['filename']} subido y torrent añadido a RealDebrid. La descarga ya está completada.\nEnlaces:\n" + '\n'.join(info['links']))
            os.remove(message.document.file_name)
            enviar_a_jd(info['links'])
            await bot.edit_message_text(msg.text + "\n✅ Enlaces agregados a JDownloader.",msg.chat.id, msg.message_id)
            return
        else:
            torrents_en_descarga.append({'torrent':atorrent,'user':message.chat.id})
        await bot.send_message(message.chat.id, f"Archivo '{message.document.file_name}' subido y torrent añadido a RealDebrid.")
        os.remove(message.document.file_name)
    else:
        await bot.send_message(message.chat.id, "Por favor, sube un archivo con extensión .torrent")

# Handle text messages and extract urls
@bot.message_handler(func=lambda message: True, content_types=['text'])
async def handle_text(message):
    if (message.chat.id!=superuser):
        return
    if (message.text=='/fin'):
        exit()
        return
    pattern = r'https?://\S+|www\.\S+'
    urls=re.findall(pattern, message.text)
    if urls:
        for url in urls:
            analisis=RD.unrestrict.check(url).json()
            # print(analisis)
            if ('error' in analisis):
                await bot.send_message(message.chat.id, f"URL: {url} \nError: {analisis['error']}")
                continue
            if ('supported' not in analisis) or (analisis['supported']==0):
                await bot.send_message(message.chat.id, f"URL: {url} \nNo es compatible con RealDebrid.")
                return
            descarga=RD.unrestrict.link(url).json()
            if ('error' in descarga):
                await bot.send_message(message.chat.id, f"URL: {url} \nError: {descarga['error']}")
                return
            # print(descarga)
            await bot.send_message(message.chat.id, f"Archivo: {descarga['filename']} \nEnlace original: {descarga['link']} \nEnlace directo: {descarga['download']}")
    else:
        await bot.send_message(message.chat.id, "No se encontraron URLs en el mensaje.")


async def main():
    try:
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        await bot.send_message(superuser, f"🟢 *Bot iniciado*",parse_mode='MarkdownV2',disable_notification=True)
        L = await asyncio.gather(
            tarea_de_descargas(),
            # tareas_diarias(),
            # tareas_horarias(),
            bot.polling(non_stop=True)
            )
    except Exception as e:
        await bot.send_message(superuser, "Error: " + str(e))
    finally:
        bot.close()

async def msgfin():
    await bot.send_message(superuser, f"🛑 *Bot cerrado*",parse_mode='MarkdownV2')

try:
    asyncio.run(main())
finally:
    asyncio.run(msgfin())