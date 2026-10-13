import os

from resume_parser import extract_text
from skill_extractor import extract_skills

from matcher import (
    read_job_description,
    calculate_match,
    calculate_preferred_match,
    semantic_similarity,
    calculate_experience_score,
    calculate_education_score
)

from candidate_info import extract_candidate_info


# ==========================================
# 1. RESUME FOLDER
# ==========================================

RESUME_FOLDER = "resumes"


# ==========================================
# 2. JOB DESCRIPTION
# ==========================================

JOB_DESCRIPTION_PATH = "job_description.txt"


# ==========================================
# 3. READ JOB DESCRIPTION
# ==========================================

job_text = read_job_description(
    JOB_DESCRIPTION_PATH
)


# ==========================================
# 4. SEPARATE REQUIRED AND PREFERRED SKILLS
# ==========================================

required_section = job_text.split(
    "PREFERRED SKILLS:"
)[0]

preferred_section = job_text.split(
    "PREFERRED SKILLS:"
)[1].split(
    "RESPONSIBILITIES:"
)[0]


# ==========================================
# 5. EXTRACT JOB SKILLS
# ==========================================

required_skills = extract_skills(
    required_section
)

preferred_skills = extract_skills(
    preferred_section
)


# ==========================================
# 6. GET ALL PDF FILES
# ==========================================

resume_files = [
    file
    for file in os.listdir(RESUME_FOLDER)
    if file.lower().endswith(".pdf")
]


# ==========================================
# 7. CHECK FOR RESUMES
# ==========================================

if not resume_files:

    print("\nNo PDF resumes found.")

    exit()


print("\n")
print("=" * 60)
print("        MULTIPLE RESUME SCREENING SYSTEM")
print("=" * 60)

print(
    f"\nFound {len(resume_files)} resume(s)."
)


# ==========================================
# 8. STORE RESULTS
# ==========================================

results = []


# ==========================================
# 9. PROCESS EACH RESUME
# ==========================================

for resume_file in resume_files:

    print("\n")
    print("=" * 60)

    print(
        f"Processing: {resume_file}"
    )

    print("=" * 60)


    # --------------------------------------
    # Resume path
    # --------------------------------------

    resume_path = os.path.join(
        RESUME_FOLDER,
        resume_file
    )


    # --------------------------------------
    # Extract resume text
    # --------------------------------------

    # Your resume_parser.py uses extract_text()
    resume_text = extract_text(
        resume_path
    )


    # --------------------------------------
    # Validate extracted text
    # --------------------------------------

    if not resume_text or not resume_text.strip():

        print(
            f"⚠️ Unable to extract readable text "
            f"from {resume_file}"
        )

        print(
            "Skipping this resume."
        )

        continue


    # --------------------------------------
    # Extract candidate skills
    # --------------------------------------

    candidate_skills = extract_skills(
        resume_text
    )


    # --------------------------------------
    # Extract candidate information
    # --------------------------------------

    candidate_info = extract_candidate_info(
        resume_text
    )


    # --------------------------------------
    # Required skill match
    # --------------------------------------

    (
        match_score,
        matched_skills,
        missing_skills
    ) = calculate_match(
        candidate_skills,
        required_skills
    )


    # --------------------------------------
    # Preferred skill match
    # --------------------------------------

    (
        preferred_score,
        matched_preferred,
        missing_preferred
    ) = calculate_preferred_match(
        candidate_skills,
        preferred_skills
    )


    # --------------------------------------
    # Semantic AI score
    # --------------------------------------

    semantic_score = semantic_similarity(
        resume_text,
        job_text
    )


    # --------------------------------------
    # Experience score
    # --------------------------------------

    experience_score = calculate_experience_score(
        candidate_info["Experience"],
        job_text
    )


    # --------------------------------------
    # Education score
    # --------------------------------------

    education_score = calculate_education_score(
        candidate_info["Education"],
        job_text
    )


    # --------------------------------------
    # Overall AI score
    # --------------------------------------

    overall_score = (
        (match_score * 0.45)
        +
        (preferred_score * 0.10)
        +
        (semantic_score * 0.20)
        +
        (experience_score * 0.15)
        +
        (education_score * 0.10)
    )


    # --------------------------------------
    # Store result
    # --------------------------------------

    results.append({

        "file": resume_file,

        "name": candidate_info["Name"],

        "required_score": match_score,

        "preferred_score": preferred_score,

        "semantic_score": semantic_score,

        "experience_score": experience_score,

        "education_score": education_score,

        "overall_score": overall_score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills
    })


# ==========================================
# 10. CHECK RESULTS
# ==========================================

if not results:

    print("\n")
    print("=" * 60)
    print("       NO READABLE RESUMES FOUND")
    print("=" * 60)

    print(
        "\nThe PDF files were found, but no readable "
        "resume text could be extracted."
    )

    print(
        "\nPlease add text-based PDF resumes "
        "or OCR support."
    )

    exit()


# ==========================================
# 11. SORT CANDIDATES
# ==========================================

results.sort(
    key=lambda x: x["overall_score"],
    reverse=True
)


# ==========================================
# 12. DISPLAY CANDIDATE RESULTS
# ==========================================

print("\n")
print("=" * 60)
print("             CANDIDATE RESULTS")
print("=" * 60)


for candidate in results:

    print("\n")

    print(
        f"Candidate: "
        f"{candidate['name']}"
    )

    print(
        f"File: "
        f"{candidate['file']}"
    )

    print(
        f"Required Skills: "
        f"{candidate['required_score']:.2f}%"
    )

    print(
        f"Preferred Skills: "
        f"{candidate['preferred_score']:.2f}%"
    )

    print(
        f"Semantic AI: "
        f"{candidate['semantic_score']:.2f}%"
    )

    print(
        f"Experience: "
        f"{candidate['experience_score']:.2f}%"
    )

    print(
        f"Education: "
        f"{candidate['education_score']:.2f}%"
    )

    print(
        f"OVERALL SCORE: "
        f"{candidate['overall_score']:.2f}%"
    )

    print(
        f"Matched Skills: "
        f"{', '.join(sorted(candidate['matched_skills']))}"
    )

    print(
        f"Missing Skills: "
        f"{', '.join(sorted(candidate['missing_skills']))}"
    )

    print("-" * 60)


# ==========================================
# 13. SCREENING COMPLETE
# ==========================================

print("\n")
print("=" * 60)
print("       MULTIPLE RESUME SCREENING COMPLETE")
print("=" * 60)
