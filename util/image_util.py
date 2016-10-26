from secret import IMGUR_TOKEN
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import aiohttp as http

async def upload_to_imgur(buf: BytesIO):
    """
    Uploads a byte array to imgur

    :param buf: The byte array to upload
    :return:
    A link to the image on imgur or None if the image could not be uploaded
    """

    # Seeking to 0
    buf.seek(0)

    async with http.post('https://api.imgur.com/3/image', data={
        'image': buf,
        'type': 'file'
    }, headers={
        'authorization': 'Client-ID %s' % IMGUR_TOKEN
    }) as r:
        json = await r.json()

        # Checking if request is okay
        if json is None or not json['success']:
            return None

        return json['data']['link']

async def text_to_image(str: str):
    """
    Converts text to an image and uploads it ot imgur

    :param str: The string to convert to an image
    :return:
    A link to the image on imgur or None if the image could not be uploaded
    """

    font = ImageFont.truetype('consola.ttf', 17)

    with Image.new('RGB', (1, 1)) as img:
        ctx = ImageDraw.Draw(img)
        dim = ctx.textsize(str, font)

    with Image.new('RGB', dim, (0x2e, 0x31, 0x36)) as img:
        ctx = ImageDraw.Draw(img)
        ctx.text((0, 0), str, 0xFFFFFFE0, font)

        # Saving image
        buf = BytesIO()
        img.save(buf, 'png')
        return await upload_to_imgur(buf)
