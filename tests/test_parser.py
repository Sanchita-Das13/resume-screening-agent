import sys
from pathlib import Path

# Add the project root to Python's import path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.parser import extract_resume_text


resume_path = "data/resumes/candidate_01.txt"

text = extract_resume_text(resume_path)

print("=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)

print("=" * 60)
print(f"Characters extracted: {len(text)}")