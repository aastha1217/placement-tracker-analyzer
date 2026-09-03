"""
STEP 2: Interactive filtering app using Streamlit.

WHY STREAMLIT:
This is the piece that replaces "SQL query + Power BI dashboard" with pure
Python. Streamlit turns a normal Python script into a small interactive
website: every time the user changes a dropdown/slider, Streamlit just
RE-RUNS this whole script top to bottom with the new values. That's the
one mental model you need -- there's no hidden magic beyond that.

TO RUN THIS: in your terminal (not Jupyter), run:
    streamlit run 02_app.py
It will open in your browser automatically at http://localhost:8501
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Placement Tracker Filter", layout="wide")

# ---- Load the cleaned data made by 01_load_and_clean.py ----
df = pd.read_csv("placements_by_branch.csv", parse_dates=["notice_date"])

st.title("🎓 Placement Tracker — Smart Filter")
st.caption(f"Data last refreshed: {pd.Timestamp.now().strftime('%d %b %Y, %I:%M %p')} "
           f"(re-run the scraper to update)")

# ---- SIDEBAR: this is where all filter widgets live ----
st.sidebar.header("Filters")

# Branch filter (multi-select dropdown)
all_branches = sorted(df["branch"].dropna().unique())
selected_branches = st.sidebar.multiselect(
    "Branch", options=all_branches, default=[]
)

# CGPA filter (slider) -- "show offers where cutoff <= my CGPA"
my_cgpa = st.sidebar.slider(
    "Your CGPA", min_value=0.0, max_value=10.0, value=8.0, step=0.1
)

# CTC filter (slider, in LPA)
min_ctc = st.sidebar.slider(
    "Minimum CTC (LPA)", min_value=0.0, max_value=50.0, value=0.0, step=0.5
)

# Job type filter (checkboxes via multiselect)
all_types = sorted(df["job_type"].dropna().unique())
selected_types = st.sidebar.multiselect(
    "Job Type", options=all_types, default=all_types
)

# ---- APPLY FILTERS ----
# This block is the direct Python equivalent of an SQL WHERE clause with
# multiple AND conditions.
filtered = df.copy()

if selected_branches:
    filtered = filtered[filtered["branch"].isin(selected_branches)]

# Keep offers with NO stated CGPA cutoff (NaN) OR student's CGPA falls within
# the eligible range. Most offers only have a lower cutoff (cgpa_max is NaN,
# so the upper check is skipped) -- but a few have BOTH a lower and upper
# cutoff (e.g. "6.5 - 9.5, Upper cut"), and we must respect both, or a
# high-CGPA student would be wrongly shown as eligible.
#
# When an INTERNAL CUT exists, it's the real functional cutoff a student
# needs to clear (companies often quote a lenient public criterion, then
# shortlist much more strictly at the internal cut stage) -- so we check
# against internal_cut instead of the public cgpa_min whenever it's present.
effective_min = filtered["internal_cut"].where(
    filtered["internal_cut"].notna(), filtered["cgpa_min"]
)
filtered = filtered[
    (effective_min.isna() | (effective_min <= my_cgpa))
    & (filtered["cgpa_max"].isna() | (my_cgpa <= filtered["cgpa_max"]))
]

filtered = filtered[
    filtered["ctc_max_lpa"].isna() | (filtered["ctc_max_lpa"] >= min_ctc)
]

if selected_types:
    filtered = filtered[filtered["job_type"].isin(selected_types)]

# ---- DISPLAY RESULTS ----
st.subheader(f"Matching offers: {len(filtered)}")

st.dataframe(
    filtered.sort_values("ctc_max_lpa", ascending=False)[[
        "company", "job_role", "job_type", "branch",
        "cgpa_full_display", "ctc_display", "notice_date", "selection_status"
    ]].rename(columns={
        "cgpa_full_display": "CGPA Cutoff",
        "ctc_display": "CTC",
        "selection_status": "Result Status",
    }),
    use_container_width=True,
    hide_index=True,
)

# ---- TRENDS: this is the part the official tracker does NOT show at all ----
st.markdown("---")
st.header("📈 Trends (updates live with your filters above)")

col1, col2 = st.columns(2)

with col1:
    st.write("**Offers by job type**")
    st.bar_chart(filtered["job_type"].value_counts())

with col2:
    st.write("**Top branches by number of offers**")
    st.bar_chart(filtered["branch"].value_counts().head(10))

col3, col4 = st.columns(2)

with col3:
    st.write("**CTC distribution (histogram, using range midpoints)**")
    # A histogram needs one number per offer. Since CTC is often a range
    # (e.g. "9.6-10.2 LPA"), we use the MIDPOINT purely for this chart's
    # bucketing -- the exact range is still shown correctly in the table
    # above and in the comparison table below.
    ctc_midpoint = (filtered["ctc_min_lpa"] + filtered["ctc_max_lpa"]) / 2
    st.bar_chart(ctc_midpoint.dropna().value_counts(bins=10).sort_index())

with col4:
    st.write("**Placement notices over time (weekly)**")
    weekly = (
        filtered.dropna(subset=["notice_date"])
        .set_index("notice_date")
        .resample("W")
        .size()
    )
    st.line_chart(weekly)

# ---- BRANCH COMPARISON: side-by-side, the official tracker only shows one
#      branch's stat-box at a time, not a direct comparison ----
st.markdown("---")
st.header("🆚 Compare Branches Side-by-Side")

compare_branches = st.multiselect(
    "Pick 2 or more branches to compare",
    options=all_branches,
    default=all_branches[:2] if len(all_branches) >= 2 else all_branches,
)

if len(compare_branches) >= 2:
    comparison_rows = []
    for b in compare_branches:
        sub = df[df["branch"] == b]
        has_ctc = sub["ctc_min_lpa"].notna().any()
        comparison_rows.append({
            "Branch": b,
            "Total Offers": len(sub),
            # Show the real range across all offers for this branch, not an
            # average that hides how wide packages actually vary.
            "CTC Range (LPA)": (
                f"{sub['ctc_min_lpa'].min()}-{sub['ctc_max_lpa'].max()}" if has_ctc else "N/A"
            ),
            "Companies Eligible": sub["company"].nunique(),
            "Confirmed Selected": sub["students_selected_num"].sum(),
            # Real status counts, instead of silently dropping non-numeric
            # results -- "how many are still pending" is genuinely useful.
            "Still Pending": (sub["selection_status"] == "Process Pending").sum(),
            "Cancelled/Removed": sub["selection_status"].str.contains(
                "Cancelled|Removed", case=False, na=False
            ).sum(),
        })
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True, hide_index=True)
    st.caption(
        "'Confirmed Selected' only counts offers where the source data gave an actual "
        "number. 'Still Pending' and 'Cancelled/Removed' show real status counts instead "
        "of hiding that information. When one offer lists multiple branches, its status is "
        "counted under every listed branch, so totals across branches will overlap rather "
        "than sum to one grand total."
    )
else:
    st.info("Pick at least 2 branches above to see a comparison table.")