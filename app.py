# app.py
import os
from preprocess import derive_profile, extract_text

def predict_resume_from_file(file_path: str) -> str:
    """
    Predict job role based on filename (and optionally folder/text if needed)
    """
    folder_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    
    # Extract text (optional fallback if needed)
    text = extract_text(file_path)
    
    # Get predicted profile
    profile = derive_profile(file_name, folder_name, text)
    return profile

if __name__ == "__main__":
    # Example usage
    sample_file = r"C:\Users\dolly\OneDrive\Desktop\Resume Classification Project\Resumes\Resumes\Workday_JohnDoe.docx"
    predicted_role = predict_resume_from_file(sample_file)
    print("Predicted Job Role:", predicted_role)
