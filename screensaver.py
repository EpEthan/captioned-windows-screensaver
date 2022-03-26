import arcade
from arcade_screensaver_framework.screensaver_framework import close_all_windows

from PIL import Image, ImageFont, ImageDraw, ImageFilter

import json
import random as rd
import os, os.path

APP_DATA_DIR = os.path.expanduser('~') + r"\screenSaver\\"


class ScreenSaver(arcade.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(APP_DATA_DIR + "screenSaverSettings.json", "r") as file:
            settings = json.loads(str(file.read()))
        self.src = settings["src"]
        self.cacheDir = settings["cacheDir"]
        self.cacheImgPath = self.cacheDir + "\\showing.png"
        self.delay = settings["delay"] * 60
        self.frame = 0
        self.font = APP_DATA_DIR + "rubik.ttf"

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()

        if int(self.frame) % self.delay == 0:
            self.frame = 0

            imgPath = self.choose_img()
            caption = self.get_img_caption(imgPath)
            caption = self.format_caption(caption)
            img = self.edit_img(imgPath, caption)

            self.l, self.r, self.w, self.h = self.get_lrwh(img)
            img = img.resize((self.w, self.h))

            if not os.path.exists(self.cacheDir):
                os.mkdir(self.cacheDir)
            img.save(self.cacheImgPath)

            background = arcade.load_texture(
                self.cacheImgPath, can_cache=False, img=img
            )
        else:
            background = arcade.load_texture(self.cacheImgPath, can_cache=False)

        arcade.draw_lrwh_rectangle_textured(self.l, self.r, self.w, self.h, background)

        self.frame += 1

    def on_key_press(self, symbol: int, modifiers: int):
        # TODO: handle keypresses to move forward/backward
        if symbol == arcade.key.LEFT:
            print('LEFT!')
        elif symbol == arcade.key.RIGHT:
            print('RIGHT!')
        else:
            close_all_windows()


    def choose_img(self, src: str = None):
        if src == None:
            src = self.src

        files = os.listdir(src)
        while files:
            rd.shuffle(files)

            file_chosen = files[rd.randint(0, len(files) - 1)]
            files.remove(file_chosen)
            path = src + "\\" + file_chosen

            if os.path.isdir(path):
                path = self.choose_img(path)

                if path:
                    return path
            else:
                lowerPath = path.lower()
                if (
                    ".png" == lowerPath[-4:]
                    or ".jpg" == lowerPath[-4:]
                    or ".jpeg" == lowerPath[-5:]
                    or ".tiff" == lowerPath[-5:]
                    or ".gif" == lowerPath[-4:]
                ):
                    return path
                else:
                    continue

        return None

    def get_img_caption(self, path: str):
        root = self.src
        rel_path = path[len(root) :]
        rel_path = rel_path[: rel_path.rfind("\\")]

        if rel_path:
            backslashI = 0
            if rel_path.find("\\", 1) == -1:
                return rel_path[1:]

            caption = rel_path[1 : rel_path.find("\\", 1)]
            while backslashI != -1:
                backslashI = rel_path.find("\\", backslashI + 1)
                if backslashI == -1:
                    cur_path = root + rel_path
                else:
                    cur_path = root + rel_path[:backslashI]

                files = os.listdir(cur_path)
                if "screensaver.config" in files:
                    with open(cur_path + "\\" + "screensaver.config", "r") as file:
                        caption = file.read()

            return caption

        return "Unknown ¯\(°_o)/¯"

    _hebLetters = "אבגדהוזחטיכלמנסעפצקרשת"

    def format_caption(self, caption: str):
        def has_heb(s: str):
            for char in s:
                if char in self._hebLetters:
                    return True
            return False

        # check if format is needed (if hebrew letters are present in first word)
        words = caption.split(" ")
        should_reverse = has_heb(words[0])

        if not should_reverse:
            return caption

        # reverse string
        for i in range(len(words)):
            if has_heb(words[i]):
                words[i] = words[i][::-1]
        return " ".join(words[::-1])

    def edit_img(self, path, text="Lorem Ispum") -> Image:
        orgImg = Image.open(path)

        width, height = orgImg.size
        if width < height:  # vertical image -> rotate first
            orgImg = orgImg.transpose(Image.ROTATE_90)
            self.add_txt(orgImg, text, side="r")
            orgImg = orgImg.transpose(Image.ROTATE_270)
        else:
            self.add_txt(orgImg, text)

        return orgImg

    def add_txt(self, img: Image, text: str, side="l"):
        w, h = img.size

        # create text layer
        txtLayer = Image.new("RGBA", img.size)
        avg = lambda x, y: (x + y) / 2
        font_size = int(avg(h / 25, w / 35))
        font = ImageFont.truetype(self.font, font_size)

        edit = ImageDraw.Draw(txtLayer)
        if side == "r":
            x, y = w - w / 80, h - h / 60
        else:
            x, y = w / 80, h - h / 60
        edit.text((x, y), text, fill="white", anchor=f"{side}d", font=font)

        # get the text's bounding area to create the shadow
        left, upper, right, lower = txtLayer.getbbox()
        boxW = right - left
        boxH = lower - upper

        # create shadow layer
        shadowLayer = Image.new("RGBA", img.size)
        edit = ImageDraw.Draw(shadowLayer)
        edit.rounded_rectangle(
            [
                (left - boxW / 5.5, upper - boxH / 1.5),
                (right + boxW / 5.5, lower + boxH / 1.75),
            ],
            radius=17,
            fill=(0, 0, 0, 140),
        )
        shadowLayer = shadowLayer.filter(ImageFilter.GaussianBlur(radius=30))
        # shadowLayer = shadowLayer.filter(ImageFilter.GaussianBlur(radius=30))

        # add layers to original image
        shadowLayer.paste(txtLayer, (0, 0), txtLayer)
        img.paste(shadowLayer, (0, 0), shadowLayer)

    def get_lrwh(self, img: Image):
        imgWidth, imgHeight = img.size

        # img size is:
        #   scaledWidth, SCREEN_HEIGHT    OR
        #   SCREEN_WIDTH, scaledHeight
        scaleToHeight = self.height / imgHeight
        scaledWidth = int(imgWidth * scaleToHeight)

        scaleToWidth = self.width / imgWidth
        scaledHeight = int(imgHeight * scaleToWidth)

        if scaledWidth <= self.width:  # scaling fits well
            imgWidth, imgHeight = scaledWidth, self.height
        else:
            imgWidth, imgHeight = self.width, scaledHeight

        leftPadding = (self.width - imgWidth) / 2
        bottomPadding = (self.height - imgHeight) / 2

        return leftPadding, bottomPadding, imgWidth, imgHeight
