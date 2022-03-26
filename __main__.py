def main():
    from screensaver import ScreenSaver
    from arcade_screensaver_framework import screensaver_framework
    import arcade

    win = screensaver_framework.create_screensaver_window(ScreenSaver)
    # window = ScreenSaver(720, 500)
    # window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
