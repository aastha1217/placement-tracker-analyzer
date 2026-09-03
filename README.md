# Placement Tracker Analyzer 🎓

An interactive Python application for filtering and analyzing campus placement data.

## 📌 Project Overview

The placement data comes in a nested JSON structure where one placement notice can contain multiple job offers. This project cleans and transforms that raw data into an analysis-ready format and provides an interactive Streamlit application for exploring placement opportunities.

The project also adds analysis features such as CTC distribution, placement trends, and side-by-side branch comparison.

## ✨ Features

- Filter placement offers by branch
- Check offers based on your CGPA eligibility
- Explore offers based on CGPA cutoff
- Filter by minimum CTC
- Filter by job type
- Handles CGPA ranges and upper cutoffs
- Handles stricter internal CGPA cuts when available
- Preserves CTC ranges instead of converting them into a misleading average
- Preserves placement statuses such as Process Pending and Role Removed
- Interactive trend charts
- Side-by-side branch comparison

## 🛠️ Technologies Used

- Python
- Pandas
- Streamlit
- Matplotlib

## 🔄 Data Processing Pipeline

<pre>
Raw Placement JSON
        ↓
Flatten Nested Offers
        ↓
Clean CGPA, CTC and Selection Status
        ↓
Handle CGPA Ranges and Internal Cuts
        ↓
Explode Offers by Branch
        ↓
Generate Analysis-Ready CSV Files
        ↓
Streamlit Interactive Application
        ↓
Charts and Branch Comparison
</pre>

## 📁 Project Structure

<pre>
placement-tracker/
│
├── load_clean.ipynb        # Data loading and cleaning
├── fetch_data.py           # API data fetching with retry logic
├── app.py                  # Streamlit application
├── visualize.py            # Static chart generation
├── placements_data.json    # Raw placement data
├── requirements.txt
├── README.md
├── .gitignore
│
└── chart_*.png             # Generated charts
</pre>

## ▶️ How to Run

### 1. Install dependencies

`pip install -r requirements.txt`

### 2. Fetch placement data

`python fetch_data.py`

This fetches placement data from the API and saves it as `placements_data.json`.

### 3. Clean the raw data

Open `load_clean.ipynb` in Jupyter Notebook and run all cells.

This creates:

- `placements_clean.csv`
- `placements_by_branch.csv`

### 4. Run the Streamlit application

`streamlit run app.py`

### 5. Generate static charts (optional)

`python visualize.py`

## 📊 Data Cleaning Challenges

During development, several real-world data issues were handled.

### CGPA Ranges

Some offers contain ranges such as:

`6.5 - 9.5 (Upper cut)`

Both minimum and maximum CGPA are stored so that students above the upper cutoff are not incorrectly marked eligible.

### Incorrect Numbers in CGPA Text

Some text fields can contain numbers that are not CGPA values, such as years. The cleaning pipeline checks for phrases like "Not Applicable" and discards extracted values outside the valid CGPA range.

### Internal CGPA Cuts

Some companies specify a public CGPA criterion but have a stricter internal cutoff in the eligibility notes. When available, the internal cutoff is used for eligibility filtering.

### CTC Ranges

CTC values such as:

`960000 - 1020000`

are stored as minimum and maximum LPA values instead of being averaged, preserving the actual package range.

### Selection Status

The `students_selected` field can contain status text such as:

- Process Pending
- Role Removed
- Process Cancelled

This information is preserved instead of being discarded.

## 🚀 Future Improvements

- Live data updates from the placement source
- More advanced company search
- Additional placement analytics
- Deployment as a public web application
