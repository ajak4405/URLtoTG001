from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from urllib.parse import quote_plus, unquote
import math
from download_from_url import download_file, get_size
from file_handler import send_to_transfersh_async, progress
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from display_progress import progress_for_pyrogram, humanbytes
from url_uploader import leecher2
import os
import time
import datetime
import aiohttp
import asyncio
import mimetypes
from tools import execute
from ffprobe import stream_creator
from thumbnail_video import thumb_creator

async def video_renamer2(bot , u):
    
    if not u.reply_to_message:
        await u.reply_text(text=f"Reply To Your Video !\nExample:\n**/rename_video | onlyfilename**")
        return
    
    m = u.reply_to_message
    ft = m.document or m.video
    fsize = get_size(ft.file_size)
    if m.audio or m.photo or m.voice or m.location or m.contact:
        await m.reply_text(text=f"Please Reply To Video !\nMimeType: {ft.mime_type}")
        return
    else:
        tempname = "Video_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp4"
        if ft.file_name:
            oldname = ft.file_name
            oldname = oldname.replace('%40','@')
            oldname = oldname.replace('%25','_')
            oldname = oldname.replace(' ','_')
        else:
            oldname = "Video_CHATID" + str(m.chat.id) + "_DATE" + str(m.date) + ".mp4"

    if ft.mime_type.startswith("video/"):
        if not "|" in u.text:
            await u.reply_text(text=f"Please Type New Filename !\nExample:\n**/rename_video | onlyfilename**")
            return
        else:
            args = u.text.split("|")
            if len(args) <= 1:
                await u.reply_text(text=f"Please Type New Filename !\nExample:\n**/rename_video | onlyfilename**")
                return
            else:
                cmd , newname = u.text.split("|", 1)
                cmd = cmd.strip()
                if os.path.splitext(newname)[1]:
                    await u.reply_text(text=f"Dont Type Extension !\nExample:\n**/rename_video | onlyfilename**")
                    return
                else:
                    newname = newname.strip() + ".mp4"
                    msg1 = await u.reply_text(text=f"Current Filename: `{oldname}` [{fsize}]\nNew Name: `{newname}`")
                    msg2 = await u.reply_text(text=f"Trying To Download Media")
                    #if not os.path.isdir(download_path):
                    #    os.mkdir(download_path)
                    c_time = time.time()
                    file_path = await bot.download_media(
                        m,
                        file_name=tempname,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            "Downloading Status ...",
                            msg2,
                            c_time
                        )
                    )
                    if not file_path:
                        await msg1.delete()
                        await msg2.edit(f"Download Failed !")
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        return
                    else:
                        await msg2.edit(f"🌄 Generating thumbnail ...")
                        probe = await stream_creator(file_path)
                        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                        width = int(video_stream['width'] if 'width' in video_stream else 0)
                        height = int(video_stream['height'] if 'height' in video_stream else 0)
                        thumbnail = await thumb_creator(file_path)
                        duration = int(float(probe["format"]["duration"]))
                        try:
                            await msg2.edit(f"⬆️ Trying to Upload as Video ...")
                            c_time = time.time()
                            await bot.send_video(
                                chat_id=m.chat.id,
                                file_name=newname,
                                video=file_path,
                                width=width,
                                height=height,
                                duration=duration,
                                thumb=str(thumbnail),
                                caption=f"`{newname}` [{fsize}]",
                                reply_to_message_id=m.message_id,
                                progress=progress_for_pyrogram,
                                progress_args=(
                                    "⬆️ Uploading Status ...",
                                    msg2,
                                    c_time
                                )
                            )
                            await msg1.delete()
                            await msg2.delete()
                            try:
                                os.remove(file_path)
                            except:
                                pass
                        except Exception as e:
                            await msg1.delete()
                            await msg2.edit(f"❌ Uploading as Video Failed **Error:**\n\n{e}")
                            try:
                                os.remove(file_path)
                            except:
                                pass
    else:
        await m.reply_text(text=f"Please Reply To Video !\nMimeType: {ft.mime_type}")
        return
