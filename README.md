# Captioned Windows Screensaver
A windows-like photo screensaver, which also puts captions on the images

# In Order for it to Work:
1. Install requirements from `requirements.txt`.
2. Make changes to the [source code](#venv-and-some-library-code-present)
3. Add a settings JSON file to `USER-HOME\screenSaver\` (where `USER-HOME` is the home directory of the user, e.g.: `C:\Users\user\`)
   - The settings file should be called `screenSaverSettings.json` and be in the following format:
      ```json
      {
          "src": "C:\\Users\\User\\Pictures\\Wallpapers",
          "delay": 3,
          "cacheDir": "C:\\Users\\User\\Pictures\\tryMe",
          "font": "C:\\Users\\User\\Documents\\Programming\\Python\\imageTXT\\font.ttf"
      }
      ```
      where:
      - `src` - The root folder of all the pictures to be displayed.
      - `delay` - The amount of time to wait before changing the image.
      - `cacheDir` - The directory for storing the temporary edited image file.
      - `font` - The font for the captions on the images.
4. Finally, follow the instructions in the [arcade screensaver framework](https://github.com/SirGnip/arcade_screensaver_framework) to create the windows-compatible screensaver app.


## Optional: Custom Captions
The app automatically takes the top-most level folder name for the captions (unless in the root folder). For example, if the the image's path is `~\Pictures\Hawaii 2021\Maui\img.jpg`, and the root folder is `~\Pictures`, the caption for the pictures will be *Hawaii 2021*. 

If you want a different picture caption for all pictures under the picture's folder for example, add a `screensaver.config` file whose contents is simply the caption wanted.

That way, if you have the following hirarchy:

![folder-structure-light](https://github.com/EpEthan/captioned-windows-screensaver/blob/main/folder_structure_light.png?raw=false#gh-light-mode-only)
![folder-structure-dark](https://github.com/EpEthan/captioned-windows-screensaver/blob/main/folder_structure_dark.png?raw=false#gh-dark-mode-only)

- **Hawaii 2021**:
  - **Maui**: All pictures under the folder "Maui" and folders inside of it will have the caption: *"Hawaii 2021 - Maui"*.
  - **Mount Everest**: all pictures under this folder will have the caption: *"Hawaii 2021"*
- **Iceland 2018**:
  - All pictures under this folder will have the caption: *"Iceland 2018"*
- Any picture directly under the **root** folder will have the caption: *"Unknown ¯\(°_o)/¯"*



# VENV And Some Library Code Present
Of course, the requirements are in the `requirements.txt` file, however, some changes had to be made to the code from the python libraries, since they caused some issues:

### Arcade:
- https://api.arcade.academy/en/latest/
- The changes were made in order to avoid caching of images. Though caching is great for speeding things up, it caused errors for the project because edited pictuers are always kept in the same path, making Arcade think they are the same picture every time, and not replacing it. Therefore, I had to change:
  - `texture.py`: (in method: `load_texture`) never give pictures a persistant name - change it every time (randomly) to avoid using the same picture twice - Arcade doesn't allow saving two pictures with the same name, and will default to the previously saved one... In addition, the method now takes an argument `img`, to allow passing the picture to it immediately. This saves some time as in order to edit the pictures, the app also opens them using `Pillow`, so adding that option saves the app opening the file again.
  - `texture_atlas.py`: since the Texture Atlas maps the images and also caches them in a diffrenet level, when displaying many, it has no room/memory/whatever-it-is to save another one. Therefore, I made it clear up its maps when allocating more space for a new image. (in method: `allocate`)

###  Arcade Screen Saver Framework
- https://github.com/SirGnip/arcade_screensaver_framework
- In order to allow image "scrolling" (going forwards and backwards), I needed to be able to use some keys. Thus, I had to change `_make_window` to not make key-presses close the window. In addition, to control closing windows manually, I made the method `_close_all_windows` public. (Changes are in file: `screensaver_framework.py`) 
