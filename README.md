# Revenue Leak Detector

This is a Python project that reads a dental revenue CSV file and identifies possible patient balances that may need follow-up.

## Current Features

- Reads patient and claim data from a CSV file
- Filters for claims marked as `patient_due`
- Detects patient balances over 60 days old
- Calculates the total outstanding patient balance
- Finds the oldest balance
- Finds the largest balance
- Exports the filtered results to a new CSV file

## Project Structure

```text
revenue_leak_project/
  data/
    pseudo_dental_revenue_leaks.csv
  output/
    dataoutput.csv
  main.py
  README.md
```

## How to Run
- Run the script called 'main.py' in the 'src' folder
- Output should print a summary to the terminal and also a CSV report in the 'output' folder

## Important Note
- This project uses fake patient data for current testing