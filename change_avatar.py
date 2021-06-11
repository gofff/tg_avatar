import datetime as dt
import cv2
from PIL import Image, ImageDraw, ImageFont
import pytz
import sys
from typing import Tuple
import time

from telethon import TelegramClient
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.photos import DeletePhotosRequest

TZ = pytz.timezone('Europe/Moscow')

def unify_tz(utc_time: dt.datetime) -> dt.datetime:
    return utc_time.replace(tzinfo=pytz.utc).astimezone(TZ)

START_DATE = unify_tz(dt.datetime(1994, 5, 1, 21, 0))
FONT_FILE = "RibeyeMarrow-Regular.ttf"
IMG_H, IMG_W = 500, 500
WRK_H, WRK_W = 380, 380
FONT_SIZE = 68
NUM_MSG = 4
MSG_1 = "object"
MSG_2 = "lifetime:"
MSG_COLON = ' : '


def count_diff() -> Tuple[int, int]:
    diff = (unify_tz(dt.datetime.now()) - START_DATE).total_seconds()
    hours = int(diff / 3600) 
    minutes = int(diff / 60 - hours * 60)
    return hours, minutes

def form_image() -> Image:
    
    hours, minutes = count_diff()
    
    img = Image.new("RGB", (IMG_W, IMG_H))
    draw_img = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)

    msg = MSG_1
    line_w, line_h = draw_img.textsize(msg, font)
    vert_tab = (WRK_H - NUM_MSG * line_h) / (NUM_MSG - 1) + line_h
    print(line_h, NUM_MSG * line_h)
    assert vert_tab > line_h + 1
    text_y = (IMG_H - WRK_H) / 2
    text_x = (IMG_W - WRK_W) / 2 + (WRK_W - line_w) / 2
    draw_img.text((text_x, text_y), msg, (250, 250, 250), font=font)

    msg = MSG_2
    line_w, line_h = draw_img.textsize(msg, font)
    text_x = (IMG_W - WRK_W) / 2 + (WRK_W - line_w) / 2
    text_y += vert_tab
    draw_img.text((text_x, text_y), msg, (250, 250, 250), font=font)
    
    msg = f"{hours} h"
    line_w, line_h = draw_img.textsize(msg, font)
    text_x = (IMG_W - WRK_W) / 2 + (WRK_W - line_w) / 2
    text_y += vert_tab
    draw_img.text((text_x, text_y), msg, (250, 250, 250), font=font)

    msg = f"{minutes:02d} m"
    line_w, line_h = draw_img.textsize(msg, font)
    text_x = (IMG_W - WRK_W) / 2 + (WRK_W - line_w) / 2
    text_y += vert_tab
    draw_img.text((text_x, text_y), msg, (250, 250, 250), font=font)

    return img

async def change_avatar(client: TelegramClient, filename: str) -> None:
    await client(DeletePhotosRequest(await client.get_profile_photos('me')))
    file = await client.upload_file(filename)
    await client(UploadProfilePhotoRequest(file))

async def main_routine(client: TelegramClient) -> None:
    await client.connect()
    try:
        img = form_image()
        img.save("_.jpg")
        await change_avatar(client, "_.jpg")
        last_hour, last_minute = count_diff()
        while True:
            cur_hour, cur_minute = count_diff()
            print(cur_hour, cur_minute)
            if cur_minute != last_minute or cur_hour != last_hour:
                img = form_image()
                img.save("_.jpg")
                await change_avatar(client, "_.jpg")
                last_hour, last_minute = cur_hour, cur_minute
            time.sleep(0.5)
    except:
        await change_avatar(client, "main_avatar.jpg")
    finally:
        await change_avatar(client, "main_avatar.jpg")


def main_loop(api_id: int, api_hash: str) -> None:
    client = TelegramClient('anon', api_id, api_hash)
    client.loop.run_until_complete(main_routine(client))

if __name__ == "__main__":   
    api_id = int(sys.argv[1])
    api_hash = sys.argv[2]
    main_loop(api_id, api_hash)
    




