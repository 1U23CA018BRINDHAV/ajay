# preprocess.py
import os
import re
import fitz  # PyMuPDF
import docx2txt
import pandas as pd
from typing import Optional

# ---- Helper utilities ----
def _clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"\r\n", "\n", s)
    s = re.sub(r"\n+", "\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()

# ---- Extractors ----
def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        doc = fitz.open(path)
        pages = []
        for p in doc:
            try:
                pages.append(p.get_text("text") or "")
            except Exception:
                pages.append("")
        text = " ".join(pages)
    except Exception as e:
        print(f"PDF extraction failed for {path}: {e}")
    return _clean_text(text)

def extract_text_from_docx(path: str) -> str:
    try:
        text = docx2txt.process(path) or ""
    except Exception as e:
        print(f"DOCX extraction failed for {path}: {e}")
        text = ""
    return _clean_text(text)

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".doc":
        return extract_text_from_doc(file_path)
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return _clean_text(f.read())
        except Exception as e:
            print(f"TXT read failed for {file_path}: {e}")
            return ""
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return _clean_text(f.read())
        except Exception:
            return ""



# ---- Mapping & Profile derivation ----
FOLDER_CATEGORY_MAP = {
    "peoplesoft resumes": "PeopleSoft",
    "sql developer lightning insight": "SQL Developer",
    "workday resumes": "Workday"
}

PREFIX_PROFILE_MAP = {
    "react dev": "Front-End React Developer",
    "react developer": "Front-End React Developer",
    "react js developer": "UI Developer (React JS)",
    "ui-developer/ reactjs developer": "UI Developer (React JS)",
    "ui developer": "UI Developer (React JS)",
    "peoplesoft admin": "PeopleSoft Administrator",
    "peoplesoft finance": "PeopleSoft Finance Specialist",
    "peoplesoft fscm": "PeopleSoft FSCM Consultant",
    "peoplesoft dba": "PeopleSoft Database Administrator",
    "peoplesoft": "PeopleSoft Technical/Functional Consultant",
    "workday": "Workday Specialist",
    "hexaware": "Workday Specialist",
    "sql developer": "Database (SQL) Developer",
    "sql": "SQL Developer",
    "internship": "Software Intern",
    "intern": "Software Intern"
}

def _normalize_string(s: str) -> str:
    """Lowercase, remove symbols, keep alphanumerics + space"""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _match_filename_to_profile(file_name: str) -> Optional[str]:
    norm_name = _normalize_string(os.path.splitext(file_name)[0])
    for key, val in PREFIX_PROFILE_MAP.items():
        if key in norm_name:
            return val
    return None

def derive_profile(file_name: str, folder_name: str, extracted_text: str) -> str:
    """ Derive job role using folder → filename → text """
    folder_key = (folder_name or "").lower().strip()

    # 1) Folder-based mapping
    if folder_key in FOLDER_CATEGORY_MAP:
        cat = FOLDER_CATEGORY_MAP[folder_key]
        fname = file_name.lower()
        text = extracted_text.lower()

        if cat == "PeopleSoft":
            if "admin" in fname or "admin" in text:
                return "PeopleSoft Administrator"
            if "fscm" in fname or "fscm" in text:
                return "PeopleSoft FSCM Consultant"
            if "finance" in fname or "finance" in text:
                return "PeopleSoft Finance Specialist"
            if "dba" in fname or "database administrator" in text:
                return "PeopleSoft Database Administrator"
            return "PeopleSoft Technical/Functional Consultant"
        elif cat == "Workday":
            return "Workday Specialist"
        elif cat == "SQL Developer":
            return "Database (SQL) Developer"
        else:
            return cat

    # 2) Filename-based mapping
    maybe = _match_filename_to_profile(file_name)
    if maybe:
        return maybe

    # 3) Keyword-based fallback from text
    text = extracted_text.lower()
    if "react" in text:
        return "UI Developer (React JS)"
    if "peoplesoft" in text:
        if "admin" in text:
            return "PeopleSoft Administrator"
        if "dba" in text:
            return "PeopleSoft Database Administrator"
        if "fscm" in text:
            return "PeopleSoft FSCM Consultant"
        if "finance" in text or "general ledger" in text:
            return "PeopleSoft Finance Specialist"
        return "PeopleSoft Technical/Functional Consultant"
    if "workday" in text or "hcm" in text:
        return "Workday Specialist"
    if any(k in text for k in ("sql", "pl/sql", "oracle", "mysql", "postgresql", "database")):
        return "Database (SQL) Developer"
    if any(k in text for k in ("intern", "internship")):
        return "Software Intern"

    return "Other"

# ---- Main preprocess function ----
def preprocess_data(main_path: str) -> pd.DataFrame:
    rows = []
    for root, _, files in os.walk(main_path):
        for fname in files:
            path = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()
            text = extract_text(path)
            folder_basename = os.path.basename(root) or ""
            rows.append({
                "Folder": folder_basename,
                "File": fname,
                "Type": ext,
                "Path": path,
                "Text": text
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Category = folder category (default to Unknown)
    df["Category"] = df["Folder"].apply(lambda x: FOLDER_CATEGORY_MAP.get(x.lower(), "Unknown"))

    # Profile = normalized job role
    df["Profile"] = df.apply(lambda r: derive_profile(r["File"], r["Folder"], r["Text"]), axis=1)

    return df

