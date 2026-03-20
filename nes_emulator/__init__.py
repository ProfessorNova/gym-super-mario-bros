"""A modern NES emulator interface for gymnasium.

This package provides a fixed and maintained Python interface on top of the
nes-py C++ emulator library, compatible with gymnasium and NumPy 2.0+.
The compiled C++ shared library is still loaded from the installed nes-py
package.
"""
from .nes_env import NESEnv

__all__ = [NESEnv.__name__]
