"""A simple class for viewing images using pyglet."""


class ImageViewer:
    """A simple class for viewing images using pyglet."""

    def __init__(self, caption, height, width,
        monitor_keyboard=False,
        relevant_keys=None
    ):
        import threading
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError('rendering from python threads is not supported')
        import pyglet
        self.pyglet = pyglet
        self.KEY_MAP = {
            self.pyglet.window.key.ENTER: ord('\r'),
            self.pyglet.window.key.SPACE: ord(' '),
        }
        self.caption = caption
        self.height = height
        self.width = width
        self.monitor_keyboard = monitor_keyboard
        self.relevant_keys = relevant_keys
        self._window = None
        self._pressed_keys = []
        self._is_escape_pressed = False

    @property
    def is_open(self):
        return self._window is not None

    @property
    def is_escape_pressed(self):
        return self._is_escape_pressed

    @property
    def pressed_keys(self):
        return tuple(sorted(self._pressed_keys))

    def _handle_key_event(self, symbol, is_press):
        symbol = self.KEY_MAP.get(symbol, symbol)
        if symbol == self.pyglet.window.key.ESCAPE:
            self._is_escape_pressed = is_press
            return
        if self.relevant_keys is not None and symbol not in self.relevant_keys:
            return
        if is_press:
            self._pressed_keys.append(symbol)
        else:
            self._pressed_keys.remove(symbol)

    def on_key_press(self, symbol, modifiers):
        self._handle_key_event(symbol, True)

    def on_key_release(self, symbol, modifiers):
        self._handle_key_event(symbol, False)

    def open(self):
        self._window = self.pyglet.window.Window(
            caption=self.caption,
            height=self.height,
            width=self.width,
            vsync=False,
            resizable=True,
        )
        if self.monitor_keyboard:
            self._window.event(self.on_key_press)
            self._window.event(self.on_key_release)

    def close(self):
        if self.is_open:
            self._window.close()
            self._window = None

    def show(self, frame):
        if len(frame.shape) != 3:
            raise ValueError('frame should have shape with only 3 dimensions')
        if not self.is_open:
            self.open()
        self._window.clear()
        self._window.switch_to()
        self._window.dispatch_events()
        image = self.pyglet.image.ImageData(
            frame.shape[1],
            frame.shape[0],
            'RGB',
            frame.tobytes(),
            pitch=frame.shape[1] * -3
        )
        image.blit(0, 0, width=self._window.width, height=self._window.height)
        self._window.flip()


__all__ = [ImageViewer.__name__]
