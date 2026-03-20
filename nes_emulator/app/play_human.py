"""Play a gymnasium NES environment using keyboard input."""
import time

import gymnasium as gym
from pyglet import clock

from .._image_viewer import ImageViewer

_NOP = 0


def play_human(env: gym.Env, callback=None):
    """Play the environment using keyboard as a human."""
    assert isinstance(env.observation_space, gym.spaces.box.Box)
    obs_s = env.observation_space
    is_bw = len(obs_s.shape) == 2
    is_rgb = len(obs_s.shape) == 3 and obs_s.shape[2] in [1, 3]
    assert is_bw or is_rgb

    if hasattr(env, 'get_keys_to_action'):
        keys_to_action = env.get_keys_to_action()
    elif hasattr(env.unwrapped, 'get_keys_to_action'):
        keys_to_action = env.unwrapped.get_keys_to_action()
    else:
        raise ValueError('env has no get_keys_to_action method')

    viewer = ImageViewer(
        env.spec.id if env.spec is not None else env.__class__.__name__,
        env.observation_space.shape[0],
        env.observation_space.shape[1],
        monitor_keyboard=True,
        relevant_keys=set(sum(map(list, keys_to_action.keys()), [])),
    )

    done = True
    target_frame_duration = 1 / env.metadata['video.frames_per_second']
    last_frame_time = 0

    try:
        while True:
            current_frame_time = time.time()
            if last_frame_time + target_frame_duration > current_frame_time:
                continue
            last_frame_time = current_frame_time
            clock.tick()
            if done:
                done = False
                state = env.reset()
                viewer.show(env.unwrapped.screen)
            action = keys_to_action.get(viewer.pressed_keys, _NOP)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            viewer.show(env.unwrapped.screen)
            if callback is not None:
                callback(state, action, reward, done, next_state)
            state = next_state
            if viewer.is_escape_pressed:
                break
    except KeyboardInterrupt:
        pass

    viewer.close()
    env.close()


__all__ = [play_human.__name__]
