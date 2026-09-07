from pathlib import Path
import csv
import json

from src.parser import extract_resume_text
from src.scorer import (
    calculate_text_similarity,
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_final_score,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_DIR = BASE_DIR / "data" / "resumes"
JOB_DESCRIPTION_PATH = BASE_DIR / "data" / "job_description.txt"
OUTPUT_DIR = BASE_DIR / "outputs"


def get_recommendation(final_score):
    """
    Convert the final score into a recruiter-friendly
    recommendation.
    """

    if final_score >= 80:
        return "Strong Match"

    elif final_score >= 65:
        return "Good Match"

    elif final_score >= 50:
        return "Moderate Match"

    else:
        return "Low Match"


def generate_reasoning(
    matched_required,
    matched_preferred,
    detected_required,
    detected_preferred,
    experience_years,
    experience_score,
    education_score,
    semantic_score,
):
    """Generate strengths and gaps for the candidate."""

    strengths = []
    gaps = []

    # ---------------------------------------------------------
    # Required skills
    # ---------------------------------------------------------

    if detected_required:
        required_percentage = (
            len(matched_required)
            / len(detected_required)
        ) * 100

        if required_percentage >= 80:
            strengths.append(
                f"Strong required-skill coverage "
                f"({required_percentage:.1f}%)."
            )

        elif required_percentage >= 60:
            strengths.append(
                f"Good required-skill coverage "
                f"({required_percentage:.1f}%)."
            )

        else:
            gaps.append(
                f"Required-skill coverage is only "
                f"{required_percentage:.1f}%."
            )

    # ---------------------------------------------------------
    # Preferred skills
    # ---------------------------------------------------------

    if detected_preferred:
        preferred_percentage = (
            len(matched_preferred)
            / len(detected_preferred)
        ) * 100

        if preferred_percentage >= 60:
            strengths.append(
                f"Good preferred-skill coverage "
                f"({preferred_percentage:.1f}%)."
            )

        elif preferred_percentage > 0:
            strengths.append(
                f"Some preferred skills matched "
                f"({preferred_percentage:.1f}%)."
            )

        else:
            gaps.append(
                "No preferred skills were detected."
            )

    # ---------------------------------------------------------
    # Experience
    # ---------------------------------------------------------

    if experience_years is not None:

        if experience_score == 100:
            strengths.append(
                f"Experience matches the target range "
                f"({experience_years:g} years)."
            )

        elif experience_score == 75:
            gaps.append(
                f"Experience ({experience_years:g} years) "
                f"is above the target range."
            )

        elif experience_score == 50:
            gaps.append(
                f"Experience ({experience_years:g} years) "
                f"is below the target range."
            )

    else:
        gaps.append(
            "Experience could not be reliably detected."
        )

    # ---------------------------------------------------------
    # Education
    # ---------------------------------------------------------

    if education_score == 100:
        strengths.append(
            "Relevant bachelor's or master's degree detected."
        )

    else:
        gaps.append(
            "No matching bachelor's or master's degree detected."
        )

    # ---------------------------------------------------------
    # Semantic similarity
    # ---------------------------------------------------------

    if semantic_score >= 75:
        strengths.append(
            f"High semantic similarity ({semantic_score:.1f}%)."
        )

    elif semantic_score >= 50:
        strengths.append(
            f"Moderate semantic similarity ({semantic_score:.1f}%)."
        )

    else:
        gaps.append(
            f"Low semantic similarity ({semantic_score:.1f}%)."
        )

    # ---------------------------------------------------------
    # Build final reasoning
    # ---------------------------------------------------------

    reasoning_parts = []

    if strengths:
        reasoning_parts.append(
            "Strengths: " + " ".join(strengths)
        )

    if gaps:
        reasoning_parts.append(
            "Gaps: " + " ".join(gaps)
        )

    if not reasoning_parts:
        reasoning_parts.append(
            "No major strengths or gaps detected."
        )

    return " ".join(reasoning_parts)


def screen_candidate(resume_path, job_description):
    """Screen one resume and return its scoring information."""

    resume_text = extract_resume_text(resume_path)

    semantic_score = calculate_text_similarity(
        resume_text,
        job_description,
    )

    (
        skill_score,
        matched_required,
        matched_preferred,
        detected_required,
        detected_preferred,
        required_score,
        preferred_score,
    ) = calculate_skill_match(
        resume_text,
        job_description,
    )

    (
        experience_score,
        experience_years,
    ) = calculate_experience_match(
        resume_text,
    )

    education_score = calculate_education_match(
        resume_text,
    )

    final_score = calculate_final_score(
        skill_score,
        experience_score,
        education_score,
        semantic_score,
    )

    recommendation = get_recommendation(
        final_score
    )

    reasoning = generate_reasoning(
        matched_required,
        matched_preferred,
        detected_required,
        detected_preferred,
        experience_years,
        experience_score,
        education_score,
        semantic_score,
    )

    return {
        "candidate": resume_path.stem,
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "required_skill_score": required_score,
        "preferred_skill_score": preferred_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "final_score": final_score,
        "recommendation": recommendation,
        "experience_years": experience_years,
        "matched_required_skills": ", ".join(
            matched_required
        ),
        "matched_preferred_skills": ", ".join(
            matched_preferred
        ),
        "reasoning": reasoning,
    }


def main():
    """Screen all resumes and create ranked CSV and JSON files."""

    OUTPUT_DIR.mkdir(exist_ok=True)

    job_description = JOB_DESCRIPTION_PATH.read_text(
        encoding="utf-8"
    )

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
    }

    resume_files = sorted(
        [
            path
            for path in RESUME_DIR.iterdir()
            if path.suffix.lower() in supported_extensions
        ]
    )

    if not resume_files:
        print("No supported resumes found.")
        return

    results = []

    print("=" * 70)
    print("RESUME SCREENING AGENT")
    print("=" * 70)

    print(f"Found {len(resume_files)} resume(s).")
    print()

    for resume_path in resume_files:
        print(f"Screening: {resume_path.name}")

        try:
            result = screen_candidate(
                resume_path,
                job_description,
            )

            results.append(result)

        except Exception as error:
            print(
                f"Error processing {resume_path.name}: {error}"
            )

    results.sort(
        key=lambda item: item["final_score"],
        reverse=True,
    )

    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    json_path = OUTPUT_DIR / "ranked_candidates.json"

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------

    csv_path = OUTPUT_DIR / "ranked_candidates.csv"

    fieldnames = [
        "rank",
        "candidate",
        "final_score",
        "recommendation",
        "semantic_score",
        "skill_score",
        "required_skill_score",
        "preferred_skill_score",
        "experience_score",
        "education_score",
        "experience_years",
        "matched_required_skills",
        "matched_preferred_skills",
        "reasoning",
    ]

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:
            writer.writerow(result)

    # ---------------------------------------------------------
    # Display ranked shortlist
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("RANKED CANDIDATES")
    print("=" * 70)

    print(
        f"{'RANK':<6}"
        f"{'CANDIDATE':<18}"
        f"{'SCORE':<10}"
        f"RECOMMENDATION"
    )

    print("-" * 70)

    for result in results:

        print(
            f"{result['rank']:<6}"
            f"{result['candidate']:<18}"
            f"{result['final_score']:<10}"
            f"{result['recommendation']}"
        )

    print()
    print(f"CSV saved to: {csv_path}")
    print(f"JSON saved to: {json_path}")


if __name__ == "__main__":
    main()