"""Play the environment making uniformly random decisions."""
from tqdm import tqdm


def play_random(env, steps):
    """Play the environment making uniformly random decisions."""
    try:
        done = True
        progress = tqdm(range(steps))
        for _ in progress:
            if done:
                _ = env.reset()
            action = env.action_space.sample()
            _, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            progress.set_postfix(reward=reward, info=info)
            env.render()
    except KeyboardInterrupt:
        pass
    env.close()


__all__ = [play_random.__name__]
