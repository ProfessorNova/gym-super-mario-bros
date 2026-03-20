"""An environment wrapper to convert binary to discrete action space."""
import gymnasium as gym
from gymnasium import Env, Wrapper


class JoypadSpace(Wrapper):
    """An environment wrapper to convert binary to discrete action space."""

    _button_map = {
        'right':  0b10000000,
        'left':   0b01000000,
        'down':   0b00100000,
        'up':     0b00010000,
        'start':  0b00001000,
        'select': 0b00000100,
        'B':      0b00000010,
        'A':      0b00000001,
        'NOOP':   0b00000000,
    }

    @classmethod
    def buttons(cls) -> list:
        return list(cls._button_map.keys())

    def __init__(self, env: Env, actions: list):
        super().__init__(env)
        self.action_space = gym.spaces.Discrete(len(actions))
        self._action_map = {}
        self._action_meanings = {}
        for action, button_list in enumerate(actions):
            byte_action = 0
            for button in button_list:
                byte_action |= self._button_map[button]
            self._action_map[action] = byte_action
            self._action_meanings[action] = ' '.join(button_list)

    def step(self, action):
        return self.env.step(self._action_map[action])

    def reset(self, **kwargs):
        return self.env.reset(**kwargs)

    def get_keys_to_action(self):
        old_keys_to_action = self.env.unwrapped.get_keys_to_action()
        action_to_keys = {v: k for k, v in old_keys_to_action.items()}
        keys_to_action = {}
        for action, byte in self._action_map.items():
            keys = action_to_keys[byte]
            keys_to_action[keys] = action
        return keys_to_action

    def get_action_meanings(self):
        actions = sorted(self._action_meanings.keys())
        return [self._action_meanings[action] for action in actions]


__all__ = [JoypadSpace.__name__]
