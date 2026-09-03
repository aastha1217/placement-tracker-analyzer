"""
STEP 3: Standalone charts using matplotlib.

WHY THIS FILE EXISTS SEPARATELY FROM THE STREAMLIT APP:
Streamlit charts only exist while the app is running in your browser.
This script saves PNG image files to disk -- useful for your GitHub README,
resume portfolio page, or a report, since you can just embed the image
without needing to run the whole app to show your findings.
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("placements_by_branch.csv", parse_dates=["notice_date"])

plt.style.use("seaborn-v0_8-whitegrid")

# ---- Chart 1: Number of offers per job type ----
fig, ax = plt.subplots(figsize=(8, 5))
df["job_type"].value_counts().plot(kind="barh", ax=ax, color="#2E86AB")
ax.set_title("Number of Offers by Job Type")
ax.set_xlabel("Number of offers")
plt.tight_layout()
plt.savefig("chart_job_type.png", dpi=150)
plt.close()

# ---- Chart 2: Top 10 branches by number of offers ----
fig, ax = plt.subplots(figsize=(8, 5))
top_branches = df["branch"].value_counts().head(10)
top_branches.plot(kind="bar", ax=ax, color="#A23B72")
ax.set_title("Top 10 Branches by Number of Offers")
ax.set_ylabel("Number of offers")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("chart_top_branches.png", dpi=150)
plt.close()

# ---- Chart 3: CTC distribution (LPA) ----
# A histogram needs one number per offer, but CTC is often a range
# (e.g. "9.6-10.2 LPA"). We use the MIDPOINT of each range purely for this
# chart's bucketing -- exact ranges are preserved in the CSV/app tables,
# this chart is only meant to show the overall shape of the distribution.
fig, ax = plt.subplots(figsize=(8, 5))
ctc_midpoint = (df["ctc_min_lpa"] + df["ctc_max_lpa"]) / 2
ctc_midpoint.dropna().plot(kind="hist", bins=20, ax=ax, color="#F18F01", edgecolor="black")
ax.set_title("Distribution of CTC Offered (LPA, range midpoints)")
ax.set_xlabel("CTC (Lakhs Per Annum)")
ax.set_ylabel("Number of offers")
plt.tight_layout()
plt.savefig("chart_ctc_distribution.png", dpi=150)
plt.close()

# ---- Chart 4: Notices over time ----
fig, ax = plt.subplots(figsize=(10, 5))
notices_over_time = df.dropna(subset=["notice_date"]).set_index("notice_date").resample("W").size()
notices_over_time.plot(ax=ax, color="#3B1F2B", marker="o")
ax.set_title("Placement Notices Over Time (Weekly)")
ax.set_ylabel("Number of notices")
plt.tight_layout()
plt.savefig("chart_notices_over_time.png", dpi=150)
plt.close()

print("Saved 4 charts:")
print("  chart_job_type.png")
print("  chart_top_branches.png")
print("  chart_ctc_distribution.png")
print("  chart_notices_over_time.png")