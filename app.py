from pathlib import Path
import json
import tempfile

import pandas as pd
import streamlit as st

from src.parser import extract_resume_text
from src.scorer import (
    calculate_text_similarity,
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_final_score,
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_recommendation(final_score):
    """Convert score into recruiter-friendly recommendation."""

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
    """Generate strengths and gaps for a candidate."""

    strengths = []
    gaps = []

    # --------------------------------------------------------
    # REQUIRED SKILLS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PREFERRED SKILLS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    if education_score == 100:

        strengths.append(
            "Relevant bachelor's or master's degree detected."
        )

    else:

        gaps.append(
            "No matching bachelor's or master's degree detected."
        )

    # --------------------------------------------------------
    # SEMANTIC SIMILARITY
    # --------------------------------------------------------

    if semantic_score >= 75:

        strengths.append(
            f"High semantic similarity "
            f"({semantic_score:.1f}%)."
        )

    elif semantic_score >= 50:

        strengths.append(
            f"Moderate semantic similarity "
            f"({semantic_score:.1f}%)."
        )

    else:

        gaps.append(
            f"Low semantic similarity "
            f"({semantic_score:.1f}%)."
        )

    # --------------------------------------------------------
    # BUILD REASONING
    # --------------------------------------------------------

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


# ============================================================
# SCREEN ONE CANDIDATE
# ============================================================

def screen_candidate(resume_path, job_description):
    """Screen one resume."""

    resume_text = extract_resume_text(
        resume_path
    )

    # Semantic similarity
    semantic_score = calculate_text_similarity(
        resume_text,
        job_description,
    )

    # Skill matching
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

    # Experience
    (
        experience_score,
        experience_years,
    ) = calculate_experience_match(
        resume_text,
    )

    # Education
    education_score = calculate_education_match(
        resume_text
    )

    # Final score
    final_score = calculate_final_score(
        skill_score,
        experience_score,
        education_score,
        semantic_score,
    )

    # Recommendation
    recommendation = get_recommendation(
        final_score
    )

    # Reasoning
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


# ============================================================
# HEADER
# ============================================================

st.title("📄 AI Resume Screening Agent")

st.markdown(
    """
### Intelligent Resume Screening & Candidate Ranking

Upload a **Job Description** and multiple resumes.

The system uses:

- NLP semantic similarity
- Required skill matching
- Preferred skill matching
- Experience matching
- Education matching

to automatically rank candidates.
"""
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Screening Settings")

    st.info(
        """
**Scoring Model**

Skills — 50%

Experience — 25%

Education — 15%

Semantic Similarity — 10%
"""
    )

    st.markdown("### Recommendation")

    st.write("🟢 Strong Match: 80–100")

    st.write("🔵 Good Match: 65–79")

    st.write("🟡 Moderate Match: 50–64")

    st.write("🔴 Low Match: Below 50")


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.header("1️⃣ Job Description")

job_description_file = st.file_uploader(
    "Upload Job Description",
    type=["txt"],
    help="Upload a .txt file containing the job description.",
)

job_description = ""


if job_description_file is not None:

    job_description = (
        job_description_file
        .read()
        .decode(
            "utf-8",
            errors="ignore"
        )
    )

    st.success(
        "Job description uploaded successfully."
    )

    with st.expander(
        "View Job Description"
    ):

        st.text(job_description)


else:

    default_jd_path = (
        BASE_DIR
        / "data"
        / "job_description.txt"
    )

    if default_jd_path.exists():

        job_description = (
            default_jd_path.read_text(
                encoding="utf-8"
            )
        )

        st.info(
            "No JD uploaded. Using the sample job "
            "description from data/job_description.txt."
        )


# ============================================================
# RESUME UPLOAD
# ============================================================

st.header("2️⃣ Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload one or more resumes",
    type=[
        "pdf",
        "docx",
        "txt",
    ],
    accept_multiple_files=True,
    help="You can upload 10+ resumes in one run.",
)


if uploaded_files:

    st.success(
        f"{len(uploaded_files)} resume(s) uploaded."
    )

    st.write("Uploaded resumes:")

    for uploaded_file in uploaded_files:

        st.write(
            f"• {uploaded_file.name}"
        )


# ============================================================
# SCREEN BUTTON
# ============================================================

st.divider()

screen_button = st.button(
    "🚀 Screen Resumes",
    type="primary",
    use_container_width=True,
)


# ============================================================
# PROCESS RESUMES
# ============================================================

if screen_button:

    if not job_description.strip():

        st.error(
            "Please upload a Job Description or make sure "
            "data/job_description.txt exists."
        )

    elif not uploaded_files:

        st.error(
            "Please upload at least one resume."
        )

    else:

        results = []

        progress_bar = st.progress(0)

        status_text = st.empty()

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            status_text.write(
                f"Screening: {uploaded_file.name}"
            )

            suffix = Path(
                uploaded_file.name
            ).suffix

            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = Path(
                    temp_file.name
                )

            try:

                result = screen_candidate(
                    temp_path,
                    job_description,
                )

                # =================================================
                # IMPORTANT FIX
                #
                # Use the original uploaded filename instead of
                # the temporary filename generated by Python.
                # =================================================

                result["candidate"] = Path(
                    uploaded_file.name
                ).stem

                results.append(result)

            except Exception as error:

                st.error(
                    f"Error processing "
                    f"{uploaded_file.name}: {error}"
                )

            finally:

                if temp_path.exists():

                    temp_path.unlink()

            progress_bar.progress(
                (index + 1)
                / len(uploaded_files)
            )

        status_text.empty()

        # Sort by final score
        results.sort(
            key=lambda item: item["final_score"],
            reverse=True,
        )

        # Add rank
        for rank, result in enumerate(
            results,
            start=1,
        ):

            result["rank"] = rank

        # Save results in Streamlit session
        st.session_state[
            "screening_results"
        ] = results

        st.success(
            f"Screening completed successfully for "
            f"{len(results)} candidate(s)."
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "screening_results" in st.session_state:

    results = st.session_state[
        "screening_results"
    ]

    st.divider()

    st.header("3️⃣ Ranked Candidates")


    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    strong_matches = sum(
        1
        for result in results
        if result["recommendation"]
        == "Strong Match"
    )

    good_matches = sum(
        1
        for result in results
        if result["recommendation"]
        == "Good Match"
    )

    moderate_matches = sum(
        1
        for result in results
        if result["recommendation"]
        == "Moderate Match"
    )

    low_matches = sum(
        1
        for result in results
        if result["recommendation"]
        == "Low Match"
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Total Candidates",
        len(results),
    )

    col2.metric(
        "Strong Matches",
        strong_matches,
    )

    col3.metric(
        "Good Matches",
        good_matches,
    )

    col4.metric(
        "Low Matches",
        low_matches,
    )


    # ========================================================
    # RANKING TABLE
    # ========================================================

    table_data = []

    for result in results:

        table_data.append(
            {
                "Rank": result["rank"],
                "Candidate": result["candidate"],
                "Final Score": result["final_score"],
                "Recommendation": result[
                    "recommendation"
                ],
                "Skills": result["skill_score"],
                "Experience": result[
                    "experience_score"
                ],
                "Education": result[
                    "education_score"
                ],
                "Semantic": result[
                    "semantic_score"
                ],
            }
        )


    dataframe = pd.DataFrame(
        table_data
    )


    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    st.header("4️⃣ Candidate Details")


    for result in results:

        title = (
            f"#{result['rank']} "
            f"{result['candidate']} — "
            f"{result['final_score']}% "
            f"({result['recommendation']})"
        )


        with st.expander(title):

            col1, col2, col3, col4 = st.columns(4)


            col1.metric(
                "Final Score",
                f"{result['final_score']}%",
            )


            col2.metric(
                "Skill Score",
                f"{result['skill_score']}%",
            )


            if result["experience_years"] is not None:

                experience_text = (
                    f"{result['experience_years']} years"
                )

            else:

                experience_text = "Not detected"


            col3.metric(
                "Experience",
                experience_text,
            )


            col4.metric(
                "Semantic Similarity",
                f"{result['semantic_score']}%",
            )


            st.markdown(
                "### Recommendation"
            )

            st.write(
                result["recommendation"]
            )


            st.markdown(
                "### Required Skill Score"
            )

            st.write(
                f"{result['required_skill_score']}%"
            )


            st.markdown(
                "### Preferred Skill Score"
            )

            st.write(
                f"{result['preferred_skill_score']}%"
            )


            st.markdown(
                "### Matched Required Skills"
            )


            if result[
                "matched_required_skills"
            ]:

                st.write(
                    result[
                        "matched_required_skills"
                    ]
                )

            else:

                st.write(
                    "None detected."
                )


            st.markdown(
                "### Matched Preferred Skills"
            )


            if result[
                "matched_preferred_skills"
            ]:

                st.write(
                    result[
                        "matched_preferred_skills"
                    ]
                )

            else:

                st.write(
                    "None detected."
                )


            st.markdown(
                "### Reasoning"
            )

            st.write(
                result["reasoning"]
            )


# ============================================================
# EXPORT RESULTS
# ============================================================

if "screening_results" in st.session_state:

    results = st.session_state[
        "screening_results"
    ]

    st.divider()

    st.header("5️⃣ Export Results")


    export_data = []


    for result in results:

        export_data.append(
            {
                "rank": result["rank"],
                "candidate": result["candidate"],
                "final_score": result[
                    "final_score"
                ],
                "recommendation": result[
                    "recommendation"
                ],
                "semantic_score": result[
                    "semantic_score"
                ],
                "skill_score": result[
                    "skill_score"
                ],
                "required_skill_score": result[
                    "required_skill_score"
                ],
                "preferred_skill_score": result[
                    "preferred_skill_score"
                ],
                "experience_score": result[
                    "experience_score"
                ],
                "education_score": result[
                    "education_score"
                ],
                "experience_years": result[
                    "experience_years"
                ],
                "matched_required_skills": result[
                    "matched_required_skills"
                ],
                "matched_preferred_skills": result[
                    "matched_preferred_skills"
                ],
                "reasoning": result[
                    "reasoning"
                ],
            }
        )


    export_dataframe = pd.DataFrame(
        export_data
    )


    csv_data = export_dataframe.to_csv(
        index=False
    )


    json_data = json.dumps(
        results,
        indent=4,
    )


    col1, col2 = st.columns(2)


    with col1:

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="ranked_candidates.csv",
            mime="text/csv",
            use_container_width=True,
        )


    with col2:

        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name="ranked_candidates.json",
            mime="application/json",
            use_container_width=True,
        )