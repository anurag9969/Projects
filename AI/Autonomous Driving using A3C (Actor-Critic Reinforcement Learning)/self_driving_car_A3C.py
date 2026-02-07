import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
import torch.multiprocessing as mp
import torch.nn.functional as F
import numpy as np
from torch.distributions import Normal
import cv2
import os

# ========== Hyperparameters ==========
ENV_NAME = "CarRacing-v2"
GAMMA = 0.99
LR = 1e-4
ENTROPY_BETA = 0.001
UPDATE_STEPS = 20
NUM_WORKERS = 4
MAX_EPISODES = 2000

device = torch.device("cpu")  # A3C typically CPU-based


# ========== Preprocessing ==========
def preprocess(state):
    state = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
    state = cv2.resize(state, (84, 84))
    state = state / 255.0
    return torch.tensor(state, dtype=torch.float32).unsqueeze(0)


# ========== Actor-Critic Network ==========
class ActorCritic(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.ReLU()
        )

        self.fc = nn.Linear(64 * 7 * 7, 512)

        # Actor outputs mean + std
        self.mu = nn.Linear(512, 3)
        self.sigma = nn.Linear(512, 3)

        # Critic
        self.value = nn.Linear(512, 1)

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc(x))

        mu = torch.tanh(self.mu(x))
        sigma = F.softplus(self.sigma(x)) + 1e-5
        value = self.value(x)

        return mu, sigma, value


# ========== Worker ==========
class Worker(mp.Process):
    def __init__(self, global_model, optimizer, global_ep):
        super().__init__()
        self.global_model = global_model
        self.optimizer = optimizer
        self.local_model = ActorCritic()
        self.env = gym.make(ENV_NAME)
        self.global_ep = global_ep

    def run(self):
        while self.global_ep.value < MAX_EPISODES:
            state, _ = self.env.reset()
            state = preprocess(state)

            done = False
            total_reward = 0
            log_probs = []
            values = []
            rewards = []
            entropies = []

            while not done:
                mu, sigma, value = self.local_model(state)
                dist = Normal(mu, sigma)
                action = dist.sample()
                log_prob = dist.log_prob(action).sum(dim=1)
                entropy = dist.entropy().sum(dim=1)

                next_state, reward, done, _, _ = self.env.step(action.squeeze().detach().numpy())
                next_state = preprocess(next_state)

                total_reward += reward

                log_probs.append(log_prob)
                values.append(value)
                rewards.append(torch.tensor([reward], dtype=torch.float32))
                entropies.append(entropy)

                if len(rewards) >= UPDATE_STEPS or done:
                    self.update(next_state, done, log_probs, values, rewards, entropies)
                    log_probs, values, rewards, entropies = [], [], [], []

                state = next_state

            with self.global_ep.get_lock():
                self.global_ep.value += 1
                print(f"Episode {self.global_ep.value} | Reward: {total_reward}")

    def update(self, next_state, done, log_probs, values, rewards, entropies):
        if done:
            R = torch.zeros(1, 1)
        else:
            _, _, R = self.local_model(next_state)

        returns = []
        for r in rewards[::-1]:
            R = r + GAMMA * R
            returns.insert(0, R)

        returns = torch.cat(returns)
        values = torch.cat(values)
        log_probs = torch.cat(log_probs)
        entropies = torch.cat(entropies)

        advantage = returns - values

        actor_loss = -(log_probs * advantage.detach()).mean()
        critic_loss = advantage.pow(2).mean()
        entropy_loss = -ENTROPY_BETA * entropies.mean()

        loss = actor_loss + 0.5 * critic_loss + entropy_loss

        self.optimizer.zero_grad()
        loss.backward()

        for local_param, global_param in zip(self.local_model.parameters(),
                                             self.global_model.parameters()):
            global_param._grad = local_param.grad

        self.optimizer.step()
        self.local_model.load_state_dict(self.global_model.state_dict())


# ========== Main ==========
def main():
    global_model = ActorCritic()
    global_model.share_memory()

    optimizer = optim.Adam(global_model.parameters(), lr=LR)
    global_ep = mp.Value('i', 0)

    workers = [Worker(global_model, optimizer, global_ep)
               for _ in range(NUM_WORKERS)]

    for w in workers:
        w.start()

    for w in workers:
        w.join()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()
