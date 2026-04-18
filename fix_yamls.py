import yaml
import os
import glob

# Remove 'Mock' from all scheme names manually just to clean up names if they still have them despite best efforts.
for file in glob.glob("schemes/*.yaml"):
    with open(file, "r") as f:
        data = yaml.safe_load(f)
    if "Mock " in data.get("name", ""):
        data["name"] = data["name"].replace("Mock ", "")
        with open(file, "w") as f:
            yaml.dump(data, f, sort_keys=False)
            print(f"Fixed {file}")
