from asyncio import exceptions
from email.mime import image
import arcade
from arcade_screensaver_framework.screensaver_framework import close_all_windows

from PIL import Image, ImageFont, ImageDraw, ImageFilter

import json
import random as rd
import os, os.path

APP_DATA_DIR = os.path.expanduser("~") + r"\screenSaver\\"


class ScreenSaver(arcade.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # get app settings
        with open(APP_DATA_DIR + "screenSaverSettings.json", "r") as file:
            settings = json.loads(str(file.read()))
        self.src = settings["src"]
        self.cacheDir = settings["cacheDir"]
        self.cacheImgPath = self.cacheDir + "\\showing.png"
        self.delay = settings["delay"] * 60  # 60 'frames' is about one second
        self.frame = 0
        self.font = APP_DATA_DIR + "mplus-rounded.ttf"

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()

        if int(self.frame) % self.delay == 0:
            self.frame = 0

            try:
                # get and add text to the image
                imgPath = self.choose_img()
                caption = self.get_img_caption(imgPath)
                caption = self.format_caption(caption)
                img = self.edit_img(imgPath, caption)

                # determine the size and location of the image
                self.l, self.r, self.w, self.h = self.get_lrwh(img)
                img = img.resize((self.w, self.h))

                # save the image in the "cache" folder
                if not os.path.exists(self.cacheDir):
                    os.mkdir(self.cacheDir)
                img.save(self.cacheImgPath)

                # load the texture from the image
                background = arcade.load_texture(
                    self.cacheImgPath, can_cache=False, img=img
                )
            except Exception as e:
                # ignore exception and retry choosing image
                print(e)
                self.frame -= 1
        else:
            background = arcade.load_texture(self.cacheImgPath, can_cache=False)

        # place the texture background
        arcade.draw_lrwh_rectangle_textured(self.l, self.r, self.w, self.h, background)

        self.frame += 1

    def on_key_press(self, symbol: int, modifiers: int):
        # TODO: handle keypresses to move forward/backward
        if symbol == arcade.key.LEFT:
            print("LEFT!")
        elif symbol == arcade.key.RIGHT:
            print("RIGHT!")
        else:
            close_all_windows()

    def choose_img(self, src: str = None):
        """
        Choose a random image from a given source path

        :param str src: The source path of the folder to choose the image file from.
        """

        if src == None:
            src = self.src

        files = os.listdir(src)
        while (
            files
        ):  # work until there's no more files in the folder (return if found a good file)
            # shuffle the list and choose a random file
            rd.shuffle(files)
            file_chosen = files[rd.randint(0, len(files) - 1)]
            path = src + "\\" + file_chosen

            if os.path.isdir(path):
                # get a file from the given folder
                path = self.choose_img(path)

                if path:
                    return path
            else:
                # check if the file is an image file and return it
                lowerPath = path.lower()
                if (
                    ".png" == lowerPath[-4:]
                    or ".jpg" == lowerPath[-4:]
                    or ".jpeg" == lowerPath[-5:]
                    or ".tiff" == lowerPath[-5:]
                    or ".gif" == lowerPath[-4:]
                ):
                    return path

            # remove file from the dir-list and pick a different one
            files.remove(file_chosen)

        return None

    def get_img_caption(self, path: str):
        """
        Get the most appropriate caption for the file.
        Will return the top-most level folder name (unless in the root folder),
        or the latest `screensaver.config` file contents if one exists.

        Go to Github: <https://github.com/EpEthan/captioned-windows-screensaver#optional-custom-captions>
        for more details.

        :param str path: The path to the image.
        """

        # get the relative path from the root folder to the image's folder
        root = self.src
        rel_path = path[len(root) :]
        rel_path = rel_path[: rel_path.rfind("\\")]

        if rel_path:
            # set the default caption to be the top-level folder's name
            backslashI = rel_path.find("\\", 1)
            if backslashI == -1:
                caption = rel_path[1:]
            else:
                caption = rel_path[1 : rel_path.find("\\", 1)]

            # search for the bottom-most config file and set the caption to its contents
            # (every loop we add the next part of the path and search there)
            firstLoop = True
            while backslashI != -1 or firstLoop:
                if firstLoop:
                    firstLoop = False

                # get the new path to search in
                backslashI = rel_path.find("\\", backslashI + 1)
                if backslashI == -1:
                    cur_path = root + rel_path
                else:
                    cur_path = root + rel_path[:backslashI]

                # check for a config file
                files = os.listdir(cur_path)
                if "screensaver.config" in files:
                    with open(cur_path + "\\" + "screensaver.config", "r") as file:
                        caption = file.read()

            return caption

        return "Unknown ¯\(°_o)/¯"

    _hebLetters = "אבגדהוזחטיכלמנסעפצקרשת"

    def format_caption(self, caption: str):
        """
        Format the caption text to work with rtl/ltr text.

        Flip each Hebrew word, and flip the entire order of words if the
        first word is Hebrew.

        :param str caption: The caption to be formatted.
        """

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
        """
        Add text and shadow to images in the right place.

        The text & shadow are added horizontally on the bottom-left of
        horizontal images, and vertically on the bottom-left of
        verticle pictures.

        :param str path: The path to the image in question.
        :param str text: The text to put on the image.
        """

        orgImg = Image.open(path)

        width, height = orgImg.size
        if width < height:  # vertical image -> rotate first
            orgImg = orgImg.transpose(Image.ROTATE_90)
            self.add_txt(orgImg, text, side="r")
            orgImg = orgImg.transpose(Image.ROTATE_270)
        else:
            self.add_txt(orgImg, text, side="l")

        return orgImg

    def add_txt(self, img: Image, text: str, side="l"):
        """
        Add text to the image on the bottom left/right of a given iamge.

        :param PIL.Image img: The image to add the text to.
        :param str text: The text to write on the image.
        :param str side: Either 'r' for bottom-right, or 'l' for bottom-left.
        """

        w, h = img.size

        # create text layer
        txtLayer = Image.new("RGBA", img.size)
        avg = lambda x, y: (x + y) / 2
        font_size = avg(h / 25, w / 35)
        font = ImageFont.truetype(self.font, int(font_size))

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

        # add layers to original image
        shadowLayer.paste(txtLayer, (0, 0), txtLayer)
        img.paste(shadowLayer, (0, 0), shadowLayer)

    def get_lrwh(self, img: Image) -> tuple[float, float, int, int]:
        """
        Get the "lrwh" values to place the texture in the background.

        `l` -> distance from the left;
        `r` -> distnace from the bottom;
        `w` -> with of the picture;
        `h` -> height of the picture.
        """

        imgWidth, imgHeight = img.size

        # image's w,h are:
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

        # get l,r
        leftPadding = (self.width - imgWidth) / 2
        bottomPadding = (self.height - imgHeight) / 2

        return leftPadding, bottomPadding, imgWidth, imgHeight
