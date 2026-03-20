"""An abstraction of the NES Read-Only Memory (ROM)."""
import os
import numpy as np


class ROM:
    """An abstraction of the NES Read-Only Memory (ROM)."""

    # the magic bytes expected at the first four bytes of the header
    _MAGIC = np.array([0x4E, 0x45, 0x53, 0x1A])

    def __init__(self, rom_path):
        if not isinstance(rom_path, str):
            raise TypeError('rom_path must be of type: str.')
        if not os.path.exists(rom_path):
            raise ValueError(
                'rom_path points to non-existent file: {}.'.format(rom_path)
            )
        self.raw_data = np.fromfile(rom_path, dtype='uint8')
        if not np.array_equal(self._magic, self._MAGIC):
            raise ValueError('ROM missing magic number in header.')
        if self._zero_fill != 0:
            raise ValueError("ROM header zero fill bytes are not zero.")

    # -- Header --------------------------------------------------------------

    @property
    def header(self):
        return self.raw_data[:16]

    @property
    def _magic(self):
        return self.header[:4]

    @property
    def prg_rom_size(self):
        """Return the size of the PRG ROM in KB."""
        return 16 * int(self.header[4])

    @property
    def chr_rom_size(self):
        """Return the size of the CHR ROM in KB."""
        return 8 * int(self.header[5])

    @property
    def flags_6(self):
        return '{:08b}'.format(self.header[6])

    @property
    def flags_7(self):
        return '{:08b}'.format(self.header[7])

    @property
    def prg_ram_size(self):
        size = int(self.header[8])
        if size == 0:
            size = 1
        return 8 * size

    @property
    def flags_9(self):
        return '{:08b}'.format(self.header[9])

    @property
    def flags_10(self):
        return '{:08b}'.format(self.header[10])

    @property
    def _zero_fill(self):
        return int(self.header[11:].sum())

    # -- Header flags --------------------------------------------------------

    @property
    def mapper(self):
        return int(self.flags_7[:4] + self.flags_6[:4], 2)

    @property
    def is_ignore_mirroring(self):
        return bool(int(self.flags_6[4]))

    @property
    def has_trainer(self):
        return bool(int(self.flags_6[5]))

    @property
    def has_battery_backed_ram(self):
        return bool(int(self.flags_6[6]))

    @property
    def is_vertical_mirroring(self):
        return bool(int(self.flags_6[7]))

    @property
    def has_play_choice_10(self):
        return bool(int(self.flags_7[6]))

    @property
    def has_vs_unisystem(self):
        return bool(int(self.flags_7[7]))

    @property
    def is_pal(self):
        return bool(int(self.flags_9[7]))

    # -- ROM regions ---------------------------------------------------------

    @property
    def trainer_rom_start(self):
        return 16

    @property
    def trainer_rom_stop(self):
        return 16 + 512 if self.has_trainer else 16

    @property
    def trainer_rom(self):
        return self.raw_data[self.trainer_rom_start:self.trainer_rom_stop]

    @property
    def prg_rom_start(self):
        return self.trainer_rom_stop

    @property
    def prg_rom_stop(self):
        return self.prg_rom_start + self.prg_rom_size * 1024

    @property
    def prg_rom(self):
        try:
            return self.raw_data[self.prg_rom_start:self.prg_rom_stop]
        except IndexError:
            raise ValueError('failed to read PRG-ROM on ROM.')

    @property
    def chr_rom_start(self):
        return self.prg_rom_stop

    @property
    def chr_rom_stop(self):
        return self.chr_rom_start + self.chr_rom_size * 1024

    @property
    def chr_rom(self):
        try:
            return self.raw_data[self.chr_rom_start:self.chr_rom_stop]
        except IndexError:
            raise ValueError('failed to read CHR-ROM on ROM.')


__all__ = [ROM.__name__]
