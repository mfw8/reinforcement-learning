import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from env import OthelloGymEnv
from constants import MODEL_PATH

def train_agent(total_timesteps=20000):
    def make_env():
        return OthelloGymEnv()

    env = DummyVecEnv([make_env])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        print(f"Loaded model from {MODEL_PATH}")
        return PPO.load(MODEL_PATH)
    print("No trained model found.")
    return None
