#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bootstrap
import gym_selfx.selfx

import gym
import argparse
import torch
import os

from pathlib import Path
from gym import wrappers, logger
from gym_selfx.nn.dqn import DQN, get_screen


logger.set_level(logger.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-n", type=int, default=16, help="number of demo examples")
opt = parser.parse_args()

cuda = True if torch.cuda.is_available() else False
if cuda:
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.g

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = gym.make('selfx-billard-v0')
outdir = 'demo/selfx-billard'
env = wrappers.Monitor(env, directory=outdir, force=True)
env.seed(0)
env.reset()

init_screen = get_screen(env, device)
_, _, screen_height, screen_width = init_screen.shape
n_actions = len(env.action_space)

model_path = Path('results/selfx-billard')
policy_net = DQN(screen_height, screen_width, n_actions).to(device)
policy_net.load_state_dict(torch.load(sorted(list(model_path.glob('*.mdl')))[-1], map_location=device))


def select_action(state):
    with torch.no_grad():
        expected_reward = policy_net(state)
        return expected_reward.max(1)[1].view(1, 1)


if __name__ == '__main__':
    episode_count = opt.n
    done = False

    for i in range(episode_count):
        env.reset()
        last_screen = get_screen(env, device)
        current_screen = get_screen(env, device)
        state = torch.cat((current_screen, last_screen), dim=1)
        while True:
            action = select_action(state)
            _, _, done, _ = env.step(action)
            if done:
                break
            env.render(mode='rgb_array')

    # Close the env and write monitor result info to disk
    env.close()
