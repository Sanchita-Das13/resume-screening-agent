# Resume Screening Agent

An AI-powered Resume Screening Agent that automatically analyzes resumes against a Job Description (JD), calculates candidate relevance scores, ranks candidates, and provides recommendations with explainable reasoning.

This project was developed as part of the Rooman Technologies 24-Hour AI Agent Challenge.

---

## 1. Project Overview

Recruiters often need to review a large number of resumes for a single job opening. Manually comparing every resume with a Job Description can be time-consuming and inconsistent.

This Resume Screening Agent automates the initial screening process.

The system:

1. Reads a Job Description.
2. Parses resumes in PDF, DOCX, or TXT format.
3. Extracts resume text.
4. Compares resume content with the Job Description.
5. Matches required and preferred skills.
6. Evaluates candidate experience.
7. Checks relevant educational qualifications.
8. Calculates semantic similarity using NLP embeddings.
9. Produces a weighted final score.
10. Ranks all candidates.
11. Provides a recommendation and explanation for each candidate.
12. Exports the results as CSV and JSON.

The system can process **10 or more resumes in a single run**.

---

## 2. Features

### Resume Parsing

Supported formats:

* PDF
* DOCX
* TXT

### NLP Semantic Similarity

The system uses the **Sentence Transformers** model:

`all-MiniLM-L6-v2`

The resume and Job Description are converted into numerical embeddings. Cosine similarity is then used to measure semantic relevance.

### Skill Matching

The system checks both:

**Required skills**

* Python
* Machine Learning
* Deep Learning
* NLP
* Generative AI
* SQL
* Scikit-learn
* TensorFlow
* PyTorch
* Pandas
* NumPy

**Preferred skills**

* Large Language Models
* LLM
* RAG
* LangChain
* Hugging Face
* Vector Databases
* OpenAI API
* Docker
* Cloud

### Experience Matching

The system attempts to detect explicit experience statements and employment date ranges.

The target experience for the sample role is:

**1–3 years**

### Education Matching

The system checks for relevant bachelor's or master's degree keywords.

### Candidate Ranking

Candidates are sorted from highest to lowest final score.

### Explainable Recommendations

Each candidate receives:

* Final score
* Recommendation
* Matched required skills
* Matched preferred skills
* Experience information
* Strengths
* Gaps
* Semantic similarity

### Export

Results are exported as:

* CSV
* JSON

---

## 3. System Architecture

```text
                  Job Description
                         |
                         v
                +----------------+
                | JD Processing  |
                +----------------+
                         |
                         v
Resume Files ------> Resume Parser
(PDF/DOCX/TXT)          |
                         v
                 Extracted Text
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     Skill Match   Experience Match  Education
          |              |              |
          +--------------+--------------+
                         |
                         v
                 Semantic Similarity
                 Sentence Transformer
                         |
                         v
                  Final Score
                         |
                         v
                 Candidate Ranking
                         |
               +---------+---------+
               |                   |
               v                   v
         Recommendation        Reasoning
               |
               v
          CSV / JSON
```

---

## 4. Scoring Method

The final candidate score is calculated using four components.

| Component           | Weight |
| ------------------- | -----: |
| Skills              |    50% |
| Experience          |    25% |
| Education           |    15% |
| Semantic Similarity |    10% |

### Final Score Formula

```text
Final Score =
    Skill Score × 0.50
  + Experience Score × 0.25
  + Education Score × 0.15
  + Semantic Score × 0.10
```

### Skill Score

The skill score itself is divided into:

```text
Required Skills = 70%
Preferred Skills = 30%
```

Therefore:

```text
Skill Score =
    Required Skill Score × 0.70
  + Preferred Skill Score × 0.30
```

This gives required skills greater importance than optional skills.

---

## 5. Recommendation Thresholds

The system classifies candidates using the following thresholds:

| Score    | Recommendation |
| -------- | -------------- |
| 80–100   | Strong Match   |
| 65–79.99 | Good Match     |
| 50–64.99 | Moderate Match |
| Below 50 | Low Match      |

These thresholds are configurable in the screening code.

---

## 6. Project Structure

```text
resume-screening-agent/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── job_description.txt
│   └── resumes/
│       ├── candidate_01.txt
│       ├── candidate_02.txt
│       ├── candidate_03.txt
│       ├── candidate_04.txt
│       ├── candidate_05.txt
│       ├── candidate_06.txt
│       ├── candidate_07.txt
│       ├── candidate_08.txt
│       ├── candidate_09.txt
│       └── candidate_10.txt
│
├── outputs/
│   ├── ranked_candidates.csv
│   └── ranked_candidates.json
│
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── scorer.py
│   └── screen_resumes.py
│
└── tests/
    └── test_parser.py
```

---

## 7. Technologies Used

* Python
* Streamlit
* Sentence Transformers
* Scikit-learn
* PyMuPDF
* python-docx
* Pandas
* NumPy
* PyTorch

The application uses a local NLP model and does not require an OpenAI API key.

---

## 8. Installation

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd resume-screening-agent
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the URL of the GitHub repository.

### Step 2: Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

### Step 3: Activate the Environment

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 9. Running the Command-Line Agent

From the project root:

```powershell
python -m src.screen_resumes
```

The agent scans the resumes in:

```text
data/resumes/
```

and compares them against:

```text
data/job_description.txt
```

The ranked results are saved to:

```text
outputs/ranked_candidates.csv
outputs/ranked_candidates.json
```

---

## 10. Running the Streamlit Application

Run:

```powershell
streamlit run app.py
```

The Streamlit interface allows the user to:

1. Use the default Job Description.
2. Optionally upload another TXT Job Description.
3. Upload multiple resumes.
4. Screen all uploaded candidates.
5. View ranked results.
6. View individual candidate details.
7. Download CSV results.
8. Download JSON results.

---

## 11. Sample Job Description

The included sample role is:

**AI/ML Engineer**

The Job Description includes required skills such as:

* Python
* Machine Learning
* Deep Learning
* NLP
* Generative AI
* SQL
* Scikit-learn
* TensorFlow/PyTorch
* Pandas
* NumPy

It also includes preferred skills such as:

* LLMs
* RAG
* LangChain
* Hugging Face
* Vector Databases
* OpenAI API
* Docker
* Cloud platforms

The target experience is **1–3 years**.

---

## 12. Sample Screening Results

The sample project was tested with 10 resumes.

| Rank | Candidate    | Score | Recommendation |
| ---: | ------------ | ----: | -------------- |
|    1 | candidate_01 | 94.45 | Strong Match   |
|    2 | candidate_02 | 81.21 | Strong Match   |
|    3 | candidate_03 | 78.55 | Good Match     |
|    4 | candidate_08 | 77.82 | Good Match     |
|    5 | candidate_04 | 76.17 | Good Match     |
|    6 | candidate_07 | 72.46 | Good Match     |
|    7 | candidate_05 | 67.72 | Good Match     |
|    8 | candidate_06 | 67.70 | Good Match     |
|    9 | candidate_09 | 46.00 | Low Match      |
|   10 | candidate_10 | 21.99 | Low Match      |

The test successfully processed all **10 candidates** in a single run.

---

## 13. Output Example

Each candidate result contains information similar to:

```json
{
    "candidate": "candidate_01",
    "semantic_score": 89.0,
    "skill_score": 100.0,
    "experience_score": 100,
    "education_score": 100,
    "final_score": 94.45,
    "recommendation": "Strong Match",
    "matched_required_skills": "...",
    "matched_preferred_skills": "...",
    "reasoning": "Strengths: ..."
}
```

The exact values depend on the resume and Job Description.

---

## 14. Explainability

The system does not only return a score.

For each candidate, it explains why the candidate received that score.

Examples of strengths include:

* Strong required-skill coverage.
* Good preferred-skill coverage.
* Experience matching the target range.
* Relevant bachelor's or master's degree.
* High semantic similarity.

Examples of gaps include:

* Low required-skill coverage.
* Missing preferred skills.
* Experience below or above the target range.
* No matching degree detected.
* Low semantic similarity.

This makes the ranking easier for a recruiter to interpret.

---

## 15. Tradeoffs and Design Decisions

### Local NLP Model

The project uses `all-MiniLM-L6-v2` instead of an external LLM API.

**Advantages:**

* No API key required.
* Lower operating cost.
* Can run locally.
* More reproducible for the challenge.

**Tradeoff:**

A larger embedding model or an LLM-based approach could potentially provide stronger semantic understanding but would require more computational resources and may introduce additional cost or API dependencies.

### Weighted Scoring

The system combines several signals rather than relying only on semantic similarity.

This helps ensure that explicit job requirements such as skills, experience, and education have meaningful influence.

**Tradeoff:**

The weights are manually selected and may need to be tuned for different organizations or job roles.

### Keyword Skill Matching

Skill matching uses a predefined skill list.

**Advantages:**

* Simple.
* Fast.
* Easy to understand.
* Deterministic.

**Tradeoff:**

Keyword matching can miss synonyms or skills expressed in unusual ways.

For example, different terminology may be used to describe similar technologies.

### Experience Extraction

Experience is estimated from explicit experience statements and employment date ranges.

**Tradeoff:**

Resume formats vary considerably, so experience extraction is not guaranteed to be perfect.

### Education Matching

Education is currently identified using degree-related keywords.

**Tradeoff:**

This is simpler than building a dedicated education entity extraction system and may require improvement for complex resume formats.

---

## 16. Limitations

This project is intended as an automated initial screening assistant rather than a replacement for human recruitment decisions.

Current limitations include:

* Skill matching is primarily keyword based.
* Experience extraction may not understand every resume format.
* Education extraction uses keyword matching.
* The embedding model is relatively lightweight.
* The scoring weights are manually configured.
* Scanned/image-only PDFs may require OCR support.
* The system should not be used as the sole basis for employment decisions.

Human review should remain part of the recruitment process.

---

## 17. Future Improvements

Possible future enhancements include:

* OCR support for scanned resumes.
* More advanced named entity extraction.
* Skill synonym detection.
* Better experience calculation using month-level dates.
* Improved education extraction.
* Configurable scoring weights through the UI.
* Multiple Job Description profiles.
* Database storage of candidates.
* Candidate search and filtering.
* LLM-generated interview questions.
* Recruiter feedback and score calibration.
* Bias and fairness evaluation.
* Cloud deployment.

---

## 18. Challenge Deliverables

This project provides:

* Public GitHub repository
* README documentation
* Runnable Resume Screening Agent
* Sample Job Description
* 10 sample resumes
* Ranked CSV output
* Ranked JSON output
* NLP similarity approach
* Scoring methodology
* Explainable candidate recommendations
* Streamlit user interface
* Command-line execution

---

## 19. Conclusion

The Resume Screening Agent provides an end-to-end workflow for automatically screening and ranking resumes against a Job Description.

It combines:

**Resume Parsing + Skill Matching + Experience Matching + Education Matching + NLP Semantic Similarity + Weighted Scoring + Explainable Ranking**

The system successfully processes multiple resumes in a single run and produces structured candidate rankings that can support the initial stages of recruitment.
