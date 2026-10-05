import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from pandas.errors import EmptyDataError

API_URL = "https://itpro.lk/api/v1/jobs"

# --------------------------------------------------
# 1. Get jobs from ITPro.lk API
# --------------------------------------------------

response = requests.get(API_URL, timeout=30)
response.raise_for_status()

data = response.json()

# Convert API response to DataFrame
new_jobs = pd.DataFrame(data)

# Add collection date
collection_date = datetime.now().strftime("%Y-%m-%d")
new_jobs["collected_date"] = collection_date

print("Jobs collected from ITPro:", len(new_jobs))

# --------------------------------------------------
# 2. Create folders
# --------------------------------------------------

data_dir = Path("data")
raw_dir = data_dir / "raw"

data_dir.mkdir(exist_ok=True)
raw_dir.mkdir(exist_ok=True)

# --------------------------------------------------
# 3. Save today's raw snapshot
# --------------------------------------------------

raw_file = raw_dir / f"{collection_date}.csv"

new_jobs.to_csv(raw_file, index=False)

print("Raw snapshot saved:", raw_file)

# --------------------------------------------------
# 4. Update master dataset
# --------------------------------------------------

master_file = data_dir / "itpro_jobs.csv"

if master_file.exists() and master_file.stat().st_size > 0:

    try:
        old_jobs = pd.read_csv(master_file)

    except EmptyDataError:
        print("Master file is empty. Creating a new dataset.")
        old_jobs = pd.DataFrame()

else:
    print("Master file does not exist or is empty.")
    old_jobs = pd.DataFrame()

# Combine old + new data
if not old_jobs.empty:
    all_jobs = pd.concat(
        [old_jobs, new_jobs],
        ignore_index=True
    )
else:
    all_jobs = new_jobs.copy()

# --------------------------------------------------
# 5. Remove duplicate job IDs
# --------------------------------------------------

if "id" in all_jobs.columns:
    all_jobs = all_jobs.drop_duplicates(
        subset=["id"],
        keep="first"
    )

# --------------------------------------------------
# 6. Save master dataset
# --------------------------------------------------

all_jobs.to_csv(master_file, index=False)

print("Master dataset saved:", master_file)
print("Total unique jobs:", len(all_jobs))