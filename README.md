# Captioned Windows Screensaver
A windows-like photo screensaver, which also puts captions on the images

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
