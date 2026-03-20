"""A CTypes interface to the C++ NES environment.

Loads the compiled shared library from the installed nes-py package and
provides a gymnasium-compatible NESEnv base class with NumPy 2.0+ fixes.
"""
import ctypes
import glob
import importlib.util
import itertools
import os
import sys

import gymnasium as gym
from gymnasium.spaces import Box, Discrete
import numpy as np

from ._rom import ROM
from ._image_viewer import ImageViewer


def _find_lib():
    """Locate the compiled C++ nes_env shared library from nes-py."""
    # find nes_py package path without importing it (importing it pulls in
    # the deprecated gym package and emits warnings)
    spec = importlib.util.find_spec('nes_py')
    if spec is None or spec.submodule_search_locations is None:
        raise ImportError(
            "nes-py must be installed for its compiled C++ emulator library. "
            "Install it with: pip install nes-py"
        )
    pkg_dir = spec.submodule_search_locations[0]
    pattern = os.path.join(pkg_dir, 'lib_nes_env*')
    matches = glob.glob(pattern)
    if not matches:
        raise OSError(
            'Cannot find lib_nes_env shared library in {}'.format(pkg_dir)
        )
    return matches[0]


_LIB = ctypes.cdll.LoadLibrary(_find_lib())

# setup the argument and return types
_LIB.Width.argtypes = None
_LIB.Width.restype = ctypes.c_uint
_LIB.Height.argtypes = None
_LIB.Height.restype = ctypes.c_uint
_LIB.Initialize.argtypes = [ctypes.c_wchar_p]
_LIB.Initialize.restype = ctypes.c_void_p
_LIB.Controller.argtypes = [ctypes.c_void_p, ctypes.c_uint]
_LIB.Controller.restype = ctypes.c_void_p
_LIB.Screen.argtypes = [ctypes.c_void_p]
_LIB.Screen.restype = ctypes.c_void_p
_LIB.Memory.argtypes = [ctypes.c_void_p]
_LIB.Memory.restype = ctypes.c_void_p
_LIB.Reset.argtypes = [ctypes.c_void_p]
_LIB.Reset.restype = None
_LIB.Step.argtypes = [ctypes.c_void_p]
_LIB.Step.restype = None
_LIB.Backup.argtypes = [ctypes.c_void_p]
_LIB.Backup.restype = None
_LIB.Restore.argtypes = [ctypes.c_void_p]
_LIB.Restore.restype = None
_LIB.Close.argtypes = [ctypes.c_void_p]
_LIB.Close.restype = None

# screen dimensions
SCREEN_HEIGHT = _LIB.Height()
SCREEN_WIDTH = _LIB.Width()
SCREEN_SHAPE_24_BIT = SCREEN_HEIGHT, SCREEN_WIDTH, 3
SCREEN_SHAPE_32_BIT = SCREEN_HEIGHT, SCREEN_WIDTH, 4
SCREEN_TENSOR = ctypes.c_byte * int(np.prod(SCREEN_SHAPE_32_BIT))

RAM_VECTOR = ctypes.c_byte * 0x800
CONTROLLER_VECTOR = ctypes.c_byte * 1


class NESEnv(gym.Env):
    """An NES environment based on the LaiNES emulator."""

    metadata = {
        'render.modes': ['rgb_array', 'human'],
        'video.frames_per_second': 60,
    }

    reward_range = (-float('inf'), float('inf'))

    observation_space = Box(
        low=0,
        high=255,
        shape=SCREEN_SHAPE_24_BIT,
        dtype=np.uint8,
    )

    action_space = Discrete(256)

    def __init__(self, rom_path):
        rom = ROM(rom_path)
        if rom.prg_rom_size == 0:
            raise ValueError('ROM has no PRG-ROM banks.')
        if rom.has_trainer:
            raise ValueError('ROM has trainer. trainer is not supported.')
        _ = rom.prg_rom
        _ = rom.chr_rom
        if rom.is_pal:
            raise ValueError('ROM is PAL. PAL is not supported.')
        if rom.mapper not in {0, 1, 2, 3}:
            raise ValueError(
                'ROM has an unsupported mapper number {}.'.format(rom.mapper)
            )
        self.np_random = np.random.RandomState()
        self._rom_path = rom_path
        self._env = _LIB.Initialize(self._rom_path)
        self.viewer = None
        self._has_backup = False
        self.done = True
        self.controllers = [self._controller_buffer(p) for p in range(2)]
        self.screen = self._screen_buffer()
        self.ram = self._ram_buffer()

    def _screen_buffer(self):
        address = _LIB.Screen(self._env)
        buffer_ = ctypes.cast(address, ctypes.POINTER(SCREEN_TENSOR)).contents
        screen = np.frombuffer(buffer_, dtype='uint8')
        screen = screen.reshape(SCREEN_SHAPE_32_BIT)
        if sys.byteorder == 'little':
            screen = screen[:, :, ::-1]
        return screen[:, :, 1:]

    def _ram_buffer(self):
        address = _LIB.Memory(self._env)
        buffer_ = ctypes.cast(address, ctypes.POINTER(RAM_VECTOR)).contents
        return np.frombuffer(buffer_, dtype='uint8')

    def _controller_buffer(self, port):
        address = _LIB.Controller(self._env, port)
        buffer_ = ctypes.cast(
            address, ctypes.POINTER(CONTROLLER_VECTOR)
        ).contents
        return np.frombuffer(buffer_, dtype='uint8')

    def _frame_advance(self, action):
        self.controllers[0][:] = action
        _LIB.Step(self._env)

    def _backup(self):
        _LIB.Backup(self._env)
        self._has_backup = True

    def _restore(self):
        _LIB.Restore(self._env)

    def _will_reset(self):
        pass

    def seed(self, seed=None):
        if seed is None:
            return []
        self.np_random.seed(seed)
        return [seed]

    def reset(self, seed=None, options=None, return_info=None):
        self.seed(seed)
        self._will_reset()
        if self._has_backup:
            self._restore()
        else:
            _LIB.Reset(self._env)
        self._did_reset()
        self.done = False
        return self.screen

    def _did_reset(self):
        pass

    def step(self, action):
        if self.done:
            raise ValueError('cannot step in a done environment! call `reset`')
        self.controllers[0][:] = action
        _LIB.Step(self._env)
        reward = float(self._get_reward())
        self.done = bool(self._get_done())
        info = self._get_info()
        self._did_step(self.done)
        reward = max(self.reward_range[0], min(reward, self.reward_range[1]))
        return self.screen, reward, self.done, False, info

    def _get_reward(self):
        return 0

    def _get_done(self):
        return False

    def _get_info(self):
        return {}

    def _did_step(self, done):
        pass

    def close(self):
        if self._env is None:
            raise ValueError('env has already been closed.')
        _LIB.Close(self._env)
        self._env = None
        if self.viewer is not None:
            self.viewer.close()

    def render(self, mode='human'):
        if mode == 'human':
            if self.viewer is None:
                if self.spec is None:
                    caption = self._rom_path.split('/')[-1]
                else:
                    caption = self.spec.id
                self.viewer = ImageViewer(
                    caption=caption,
                    height=SCREEN_HEIGHT,
                    width=SCREEN_WIDTH,
                )
            self.viewer.show(self.screen)
        elif mode == 'rgb_array':
            return self.screen
        else:
            render_modes = [repr(x) for x in self.metadata['render.modes']]
            msg = 'valid render modes are: {}'.format(', '.join(render_modes))
            raise NotImplementedError(msg)

    def get_keys_to_action(self):
        buttons = np.array([
            ord('d'),  # right
            ord('a'),  # left
            ord('s'),  # down
            ord('w'),  # up
            ord('\r'), # start
            ord(' '),  # select
            ord('p'),  # B
            ord('o'),  # A
        ])
        keys_to_action = {}
        values = 8 * [[0, 1]]
        for combination in itertools.product(*values):
            byte = int(''.join(map(str, combination)), 2)
            pressed = buttons[list(map(bool, combination))]
            keys_to_action[tuple(sorted(pressed))] = byte
        return keys_to_action

    def get_action_meanings(self):
        return ['NOOP']


__all__ = [NESEnv.__name__]
