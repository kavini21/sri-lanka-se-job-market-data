import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from pandas.errors import EmptyDataError

API_URL = "https://itpro.lk/api/v1/jobs"

# Get jobs from ITPro.lk
response = requests.get(API_URL, timeout=30)
response.raise_for_status()

data = response.json()

# Convert API data to DataFrame
new_jobs = pd.DataFrame(data)

# Collection date
collection_date = datetime.now().strftime("%Y-%m-%d")
new_jobs["collected_date"] = collection_date

print("Jobs collected:", len(new_jobs))

# Create folders
data_dir = Path("data")
raw_dir = data_dir / "raw"

data_dir.mkdir(exist_ok=True)
raw_dir.mkdir(exist_ok=True)

# ------------------------------------------------
# Save today's raw snapshot
# ------------------------------------------------

raw_file = raw_dir / f"{collection_date}.csv"

new_jobs.to_csv(raw_file, index=False)

print("Raw file saved:", raw_file)

# ------------------------------------------------
# Master dataset
# ------------------------------------------------

master_file = data_dir / "itpro_jobs.csv"

if master_file.exists() and master_file.stat().st_size > 0:
    try:
        old_jobs = pd.read_csv(master_file)

    except EmptyDataError:
        print("Master file is empty.")
        old_jobs = pd.DataFrame()

else:
    print("Master file does not exist or is empty.")
    old_jobs = pd.DataFrame()

# Combine
if old_jobs.empty:
    all_jobs = new_jobs.copy()
else:
    all_jobs = pd.concat(
        [old_jobs, new_jobs],
        ignore_index=True
    )

# Remove duplicate job IDs
if "id" in all_jobs.columns:
    all_jobs = all_jobs.drop_duplicates(
        subset=["id"],
        keep="first"
    )

# Save master dataset
all_jobs.to_csv(master_file, index=False)

print("Master file saved:", master_file)
print("Total unique jobs:", len(all_jobs))