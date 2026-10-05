import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

API_URL = "https://itpro.lk/api/v1/jobs"

# Get jobs from ITPro.lk
response = requests.get(API_URL, timeout=30)
response.raise_for_status()

data = response.json()

# Convert to DataFrame
new_jobs = pd.DataFrame(data)

# Add collection date
new_jobs["collected_date"] = datetime.now().strftime("%Y-%m-%d")

# Data folder
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

master_file = data_dir / "itpro_jobs.csv"

# If existing file exists, load it
if master_file.exists():
    old_jobs = pd.read_csv(master_file)

    # Add new data
    all_jobs = pd.concat(
        [old_jobs, new_jobs],
        ignore_index=True
    )
else:
    all_jobs = new_jobs

# Remove duplicates using ITPro job ID
if "id" in all_jobs.columns:
    all_jobs = all_jobs.drop_duplicates(subset=["id"])

# Save
all_jobs.to_csv(master_file, index=False)

print(f"New jobs collected: {len(new_jobs)}")
print(f"Total unique jobs: {len(all_jobs)}")