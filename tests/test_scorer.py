import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.parser import extract_resume_text
from src.scorer import (
    calculate_text_similarity,
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_final_score,
)


resume_path = "data/resumes/candidate_01.txt"
jd_path = "data/job_description.txt"


resume_text = extract_resume_text(resume_path)

job_description = Path(jd_path).read_text(
    encoding="utf-8"
)


semantic_score = calculate_text_similarity(
    resume_text,
    job_description
)

skill_score, matched_skills, required_skills = (
    calculate_skill_match(
        resume_text,
        job_description
    )
)

experience_score, experience_years = (
    calculate_experience_match(
        resume_text
    )
)

education_score = calculate_education_match(
    resume_text
)

final_score = calculate_final_score(
    skill_score,
    experience_score,
    education_score,
    semantic_score
)


print("=" * 60)
print("RESUME SCREENING SCORE")
print("=" * 60)

print(f"Semantic Similarity : {semantic_score}%")
print(f"Skill Match         : {skill_score}%")
print(f"Experience Match    : {experience_score}%")
print(f"Education Match     : {education_score}%")
print(f"Final Score         : {final_score}%")

print()
print("Matched Skills:")
print(matched_skills)

print()
print("Required Skills:")
print(required_skills)

print()
print(f"Experience Detected: {experience_years} years")