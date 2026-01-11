# train_model.py
import os
import pandas as pd
from preprocess import preprocess_data

MAIN_PATH = r"C:\Users\dolly\OneDrive\Desktop\Resume Classification Project\Resumes\Resumes"

def main():
    print("Scanning resumes...")
    df = preprocess_data(MAIN_PATH)
    print(f"Total files processed: {len(df)}\n")

    if df.empty:
        print("No resumes found or text extraction failed.")
        return

    # Just display filename → predicted job role
    for _, row in df.iterrows():
        print(f"File: {row['File']} → Predicted Job Role: {row['Profile']}")

    # Optionally save results to Excel/CSV
    output_file = "predicted_job_roles.xlsx"
    df[["File", "Profile"]].to_excel(output_file, index=False)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
