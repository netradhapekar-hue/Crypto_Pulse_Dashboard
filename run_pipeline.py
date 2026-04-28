import subprocess

print("🚀 Starting Pipeline...\n")

# Step 1: Fetch data
print("Step 1: Fetching data...")
subprocess.run(["python", "fetch_crypto_data.py"])

# Step 2: Clean data
print("\nStep 2: Cleaning data...")
subprocess.run(["python", "data_cleaning.py"])

print("\n✅ Pipeline completed successfully!")