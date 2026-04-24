import os
import subprocess

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

print("--- Step 1: Generating Dataset ---")
subprocess.run(["python", "generate_data.py"])

print("\n--- Step 2: Training ML Models ---")
from model import train_models
train_models()

print("\n✅ Setup Complete! You can now run 'streamlit run app.py'")