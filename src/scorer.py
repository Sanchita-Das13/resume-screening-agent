import re

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# Load the NLP model once.
# This model runs locally and does not require an API key.
MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def normalize_text(text):
    """Convert text to lowercase and remove extra spaces."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_text_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between a resume
    and a job description using Sentence Transformers.
    """

    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    embeddings = MODEL.encode(
        [resume_text, job_description],
        normalize_embeddings=True
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    similarity = float(similarity)

    if similarity < 0:
        similarity = 0

    return round(similarity * 100, 2)


def calculate_skill_match(resume_text, job_description):
    """
    Calculate skill match using separate weights
    for required and preferred skills.

    Required skills = 70% of Skill Match
    Preferred skills = 30% of Skill Match
    """

    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    required_skills = [
        "python",
        "machine learning",
        "deep learning",
        "nlp",
        "generative ai",
        "sql",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
    ]

    preferred_skills = [
        "large language models",
        "llm",
        "rag",
        "langchain",
        "hugging face",
        "vector databases",
        "openai api",
        "docker",
        "cloud",
    ]

    detected_required = [
        skill
        for skill in required_skills
        if skill in job_description
    ]

    detected_preferred = [
        skill
        for skill in preferred_skills
        if skill in job_description
    ]

    matched_required = [
        skill
        for skill in detected_required
        if skill in resume_text
    ]

    matched_preferred = [
        skill
        for skill in detected_preferred
        if skill in resume_text
    ]

    if detected_required:
        required_score = (
            len(matched_required)
            / len(detected_required)
        ) * 100
    else:
        required_score = 0

    if detected_preferred:
        preferred_score = (
            len(matched_preferred)
            / len(detected_preferred)
        ) * 100
    else:
        preferred_score = 0

    skill_score = (
        required_score * 0.70
        + preferred_score * 0.30
    )

    return (
        round(skill_score, 2),
        matched_required,
        matched_preferred,
        detected_required,
        detected_preferred,
        round(required_score, 2),
        round(preferred_score, 2),
    )


def calculate_experience_match(resume_text):
    """
    Estimate candidate experience from explicit experience
    statements and employment date ranges.

    Target experience: 1-3 years.
    """

    resume_text = normalize_text(resume_text)

    # ---------------------------------------------------------
    # Method 1: Explicit experience statements
    #
    # Examples:
    # "2 years of experience"
    # "3 years experience"
    # "2.5+ years of experience"
    # ---------------------------------------------------------

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s+years?\s+of\s+experience",
        r"(\d+(?:\.\d+)?)\+?\s+years?\s+experience",
    ]

    for pattern in patterns:
        match = re.search(pattern, resume_text)

        if match:
            experience_years = float(match.group(1))

            if 1 <= experience_years <= 3:
                experience_score = 100
            elif experience_years < 1:
                experience_score = 50
            else:
                experience_score = 75

            return experience_score, experience_years

    # ---------------------------------------------------------
    # Method 2: Employment date ranges
    #
    # Examples:
    # 2024 - Present
    # 2023 - 2025
    # 2022 to 2024
    # ---------------------------------------------------------

    current_year = 2026

    date_pattern = (
        r"(20\d{2})\s*"
        r"(?:-|–|—|to)\s*"
        r"(present|20\d{2})"
    )

    matches = re.findall(
        date_pattern,
        resume_text,
        flags=re.IGNORECASE
    )

    if matches:
        total_months = 0

        for start_year, end_year in matches:
            start_year = int(start_year)

            if end_year.lower() == "present":
                end_year_value = current_year
            else:
                end_year_value = int(end_year)

            if end_year_value >= start_year:
                total_months += (
                    end_year_value - start_year
                ) * 12

        if total_months > 0:
            experience_years = round(
                total_months / 12,
                1
            )

            if 1 <= experience_years <= 3:
                experience_score = 100
            elif experience_years < 1:
                experience_score = 50
            else:
                experience_score = 75

            return experience_score, experience_years

    # ---------------------------------------------------------
    # No reliable experience found
    # ---------------------------------------------------------

    return 0, None


def calculate_education_match(resume_text):
    """
    Check whether the resume contains a relevant
    bachelor's or master's degree.
    """

    resume_text = normalize_text(resume_text)

    education_keywords = [
        "b.tech",
        "bachelor",
        "b.sc",
        "bca",
        "m.tech",
        "master",
        "m.sc",
        "mca",
    ]

    for keyword in education_keywords:
        if keyword in resume_text:
            return 100

    return 0


def calculate_final_score(
    skill_score,
    experience_score,
    education_score,
    semantic_score,
):
    """
    Calculate the final candidate score.

    Weighting:
    Skills       = 50%
    Experience   = 25%
    Education    = 15%
    Semantic     = 10%
    """

    final_score = (
        skill_score * 0.50
        + experience_score * 0.25
        + education_score * 0.15
        + semantic_score * 0.10
    )

    return round(float(final_score), 2)