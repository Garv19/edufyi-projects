import streamlit as st
import os
import tempfile
import pandas as pd
import re

from resume_parser import extract_text
from skill_extractor import extract_skills
from candidate_info import extract_candidate_info

from matcher import (
    calculate_match,
    calculate_preferred_match,
    semantic_similarity,
    calculate_experience_score,
    calculate_education_score
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 AI Resume Screening System")

st.markdown(
    "Upload resumes and a job description to automatically "
    "analyze and rank candidates using AI."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Screening Settings")

st.sidebar.info(
    """
Scoring Weights

Required Skills: 45%
Preferred Skills: 10%
Semantic AI: 20%
Experience: 15%
Education: 10%

Total: 100%
"""
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.header("📋 Job Description")

job_description_file = st.file_uploader(
    "Upload Job Description (.txt)",
    type=["txt"]
)

job_description_text = ""


if job_description_file is not None:

    job_description_text = job_description_file.read().decode(
        "utf-8",
        errors="ignore"
    )

    st.success(
        "✅ Job description uploaded successfully."
    )

else:

    default_job_file = "job_description.txt"

    if os.path.exists(default_job_file):

        try:

            with open(
                default_job_file,
                "r",
                encoding="utf-8"
            ) as file:

                job_description_text = file.read()

            st.info(
                "ℹ️ Using the existing job_description.txt file."
            )

        except Exception:

            job_description_text = ""


job_description_text = st.text_area(
    "Job Description",
    value=job_description_text,
    height=250,
    placeholder="Paste the job description here..."
)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.header("📄 Upload Resumes")

uploaded_resumes = st.file_uploader(
    "Upload one or more PDF resumes",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# SCREEN BUTTON
# ============================================================

screen_button = st.button(
    "🚀 Screen Candidates",
    type="primary",
    use_container_width=True
)


# ============================================================
# SCREENING
# ============================================================

if screen_button:

    # --------------------------------------------------------
    # VALIDATE JOB DESCRIPTION
    # --------------------------------------------------------

    if not job_description_text.strip():

        st.error(
            "❌ Please upload or enter a job description."
        )

        st.stop()


    # --------------------------------------------------------
    # VALIDATE RESUMES
    # --------------------------------------------------------

    if not uploaded_resumes:

        st.error(
            "❌ Please upload at least one resume."
        )

        st.stop()


    # ========================================================
    # EXTRACT JOB SKILLS
    # ========================================================

    all_job_skills = extract_skills(
        job_description_text
    )

    if all_job_skills is None:
        all_job_skills = []


    required_skills = []

    preferred_skills = []

    job_text_lower = job_description_text.lower()


    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    if "required skills:" in job_text_lower:

        required_section = job_text_lower.split(
            "required skills:",
            1
        )[1]

        if "preferred skills:" in required_section:

            required_section = required_section.split(
                "preferred skills:",
                1
            )[0]

        required_skills = [

            skill

            for skill in all_job_skills

            if skill.lower() in required_section

        ]


    # --------------------------------------------------------
    # ALWAYS INCLUDE PYTHON IN REQUIRED SKILLS
    # --------------------------------------------------------

    if not any(
        skill.lower() == "python"
        for skill in required_skills
    ):

        required_skills.insert(
            0,
            "Python"
        )


    # ========================================================
    # PREFERRED SKILLS
    # ========================================================

    if "preferred skills:" in job_text_lower:

        preferred_section = job_text_lower.split(
            "preferred skills:",
            1
        )[1]

        if "responsibilities:" in preferred_section:

            preferred_section = preferred_section.split(
                "responsibilities:",
                1
            )[0]

        preferred_skills = [

            skill

            for skill in all_job_skills

            if skill.lower() in preferred_section

        ]


    # ========================================================
    # JOB SKILLS DISPLAY
    # ========================================================

    st.success(
        f"✅ Found {len(uploaded_resumes)} resume(s)."
    )


    with st.expander(
        "🔎 Job Skills Detected",
        expanded=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🎯 Required Skills")

            if required_skills:

                for skill in required_skills:

                    st.write(
                        f"• {skill}"
                    )

            else:

                st.write(
                    "No required skills detected."
                )


        with col2:

            st.subheader("⭐ Preferred Skills")

            if preferred_skills:

                for skill in preferred_skills:

                    st.write(
                        f"• {skill}"
                    )

            else:

                st.write(
                    "No preferred skills detected."
                )


    st.divider()


    # ========================================================
    # PROCESS RESUMES
    # ========================================================

    results = []

    progress_bar = st.progress(0)

    status_text = st.empty()


    for index, uploaded_file in enumerate(
        uploaded_resumes
    ):

        status_text.write(
            f"🔄 Processing: {uploaded_file.name}"
        )


        # ----------------------------------------------------
        # CREATE TEMPORARY PDF
        # ----------------------------------------------------

        temp_pdf = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        temp_pdf.write(
            uploaded_file.getvalue()
        )

        temp_pdf.close()

        pdf_path = temp_pdf.name


        try:

            # =================================================
            # EXTRACT RESUME TEXT
            # =================================================

            resume_text = extract_text(
                pdf_path
            )


            if not resume_text or not resume_text.strip():

                st.warning(
                    f"⚠️ Could not extract readable text "
                    f"from {uploaded_file.name}. Skipping."
                )

                continue


            # =================================================
            # CANDIDATE INFORMATION
            # =================================================

            candidate_info = extract_candidate_info(
                resume_text
            )


            # =================================================
            # CANDIDATE NAME
            # =================================================

            candidate_name = candidate_info.get(
                "name",
                candidate_info.get(
                    "NAME",
                    ""
                )
            )


            # -------------------------------------------------
            # IF candidate_info DID NOT FIND NAME,
            # SEARCH THE RESUME TEXT DIRECTLY
            # -------------------------------------------------

            if (
                not candidate_name
                or str(candidate_name).strip().lower() == "not found"
            ):

                resume_lines = [

                    line.strip()

                    for line in resume_text.splitlines()

                    if line.strip()

                ]


                # ---------------------------------------------
                # METHOD 1:
                # NAME BEFORE "Email:"
                # ---------------------------------------------

                for line in resume_lines[:10]:

                    email_match = re.search(
                        r"^(.+?)\s+Email\s*:",
                        line,
                        re.IGNORECASE
                    )


                    if email_match:

                        possible_name = (
                            email_match.group(1).strip()
                        )


                        possible_name = re.sub(
                            r"[^A-Za-z .'-]",
                            "",
                            possible_name
                        ).strip()


                        if possible_name:

                            candidate_name = possible_name

                            break


                # ---------------------------------------------
                # METHOD 2:
                # FIRST LINE FALLBACK
                # ---------------------------------------------

                if (
                    not candidate_name
                    or str(candidate_name).strip().lower()
                    == "not found"
                ):

                    if resume_lines:

                        first_line = resume_lines[0].strip()


                        # Remove common contact information
                        first_line = re.split(
                            r"\bEmail\b\s*:",
                            first_line,
                            flags=re.IGNORECASE
                        )[0].strip()


                        first_line = re.sub(
                            r"[^A-Za-z .'-]",
                            "",
                            first_line
                        ).strip()


                        # Only accept a reasonable-looking name
                        words = first_line.split()


                        if (
                            2 <= len(words) <= 5
                            and len(first_line) <= 60
                        ):

                            candidate_name = first_line


            # -------------------------------------------------
            # FINAL FALLBACK
            # -------------------------------------------------

            if (
                not candidate_name
                or str(candidate_name).strip().lower()
                == "not found"
            ):

                filename_without_extension = os.path.splitext(
                    uploaded_file.name
                )[0]

                candidate_name = filename_without_extension


            # =================================================
            # CANDIDATE SKILLS
            # =================================================

            candidate_skills = extract_skills(
                resume_text
            )

            if candidate_skills is None:

                candidate_skills = []


            # =================================================
            # REQUIRED SKILLS
            # =================================================

            (
                required_score,
                matched_required,
                missing_required
            ) = calculate_match(
                candidate_skills,
                required_skills
            )


            # =================================================
            # PREFERRED SKILLS
            # =================================================

            (
                preferred_score,
                matched_preferred,
                missing_preferred
            ) = calculate_preferred_match(
                candidate_skills,
                preferred_skills
            )


            # =================================================
            # SEMANTIC AI
            # =================================================

            semantic_score = semantic_similarity(
                resume_text,
                job_description_text
            )


            # =================================================
            # EXPERIENCE
            # =================================================

            experience_text = candidate_info.get(
                "experience",
                candidate_info.get(
                    "EXPERIENCE",
                    "Not Found"
                )
            )


            experience_score = calculate_experience_score(
                experience_text,
                resume_text
            )


            # =================================================
            # EDUCATION
            # =================================================

            education_text = candidate_info.get(
                "education",
                candidate_info.get(
                    "EDUCATION",
                    "Not Found"
                )
            )


            education_score = calculate_education_score(
                education_text,
                resume_text
            )


            # =================================================
            # CERTIFICATIONS
            # =================================================

            certifications = candidate_info.get(
                "certifications",
                candidate_info.get(
                    "CERTIFICATIONS",
                    []
                )
            )


            # =================================================
            # ACTIVITIES
            # =================================================

            activities = candidate_info.get(
                "activities",
                candidate_info.get(
                    "ACTIVITIES",
                    []
                )
            )


            # =================================================
            # OVERALL SCORE
            # =================================================

            overall_score = (

                required_score * 0.45

                + preferred_score * 0.10

                + semantic_score * 0.20

                + experience_score * 0.15

                + education_score * 0.10

            )


            # =================================================
            # SAVE RESULT
            # =================================================

            results.append({

                "Candidate":
                    candidate_name,

                "File":
                    uploaded_file.name,

                "Required Skills":
                    required_score,

                "Preferred Skills":
                    preferred_score,

                "Semantic AI":
                    semantic_score,

                "Experience":
                    experience_score,

                "Education":
                    education_score,

                "Overall Score":
                    overall_score,

                "Matched Required":
                    matched_required,

                "Missing Required":
                    missing_required,

                "Matched Preferred":
                    matched_preferred,

                "Missing Preferred":
                    missing_preferred,

                "Experience Details":
                    experience_text,

                "Education Details":
                    education_text,

                "Certifications":
                    certifications,

                "Activities":
                    activities

            })


        except Exception as e:

            st.error(
                f"❌ Error processing "
                f"{uploaded_file.name}: {e}"
            )


        finally:

            if os.path.exists(pdf_path):

                os.remove(pdf_path)


        progress_bar.progress(
            (index + 1) / len(uploaded_resumes)
        )


    status_text.empty()


    # ========================================================
    # CHECK RESULTS
    # ========================================================

    if not results:

        st.error(
            "❌ No readable resumes were successfully processed."
        )

        st.stop()


    # ========================================================
    # SORT RESULTS
    # ========================================================

    results.sort(
        key=lambda x: x["Overall Score"],
        reverse=True
    )


    # ========================================================
    # RANKING TABLE
    # ========================================================

    display_data = []


    for rank, result in enumerate(
        results,
        start=1
    ):

        display_data.append({

            "Rank":
                rank,

            "Candidate":
                result["Candidate"],

            "Required Skills":
                f'{result["Required Skills"]:.2f}%',

            "Preferred Skills":
                f'{result["Preferred Skills"]:.2f}%',

            "Semantic AI":
                f'{result["Semantic AI"]:.2f}%',

            "Experience":
                f'{result["Experience"]:.2f}%',

            "Education":
                f'{result["Education"]:.2f}%',

            "Overall Score":
                f'{result["Overall Score"]:.2f}%'

        })


    df = pd.DataFrame(
        display_data
    )


    # ========================================================
    # CANDIDATE RANKING
    # ========================================================

    st.header("🏆 Candidate Ranking")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # TOP CANDIDATE SCORE
    # ========================================================

    top_candidate = results[0]

    st.success(
        f"🏆 Highest Overall Score: "
        f"{top_candidate['Candidate']} — "
        f"{top_candidate['Overall Score']:.2f}%"
    )


    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    st.header("👤 Candidate Details")


    for rank, result in enumerate(
        results,
        start=1
    ):

        with st.expander(
            f"#{rank} — {result['Candidate']} "
            f"({result['Overall Score']:.2f}%)"
        ):

            # ------------------------------------------------
            # SCORE CARDS
            # ------------------------------------------------

            col1, col2, col3, col4, col5 = st.columns(5)


            col1.metric(
                "Required Skills",
                f"{result['Required Skills']:.2f}%"
            )


            col2.metric(
                "Preferred Skills",
                f"{result['Preferred Skills']:.2f}%"
            )


            col3.metric(
                "Semantic AI",
                f"{result['Semantic AI']:.2f}%"
            )


            col4.metric(
                "Experience",
                f"{result['Experience']:.2f}%"
            )


            col5.metric(
                "Education",
                f"{result['Education']:.2f}%"
            )


            st.divider()


            # ------------------------------------------------
            # REQUIRED SKILLS
            # ------------------------------------------------

            skill_col1, skill_col2 = st.columns(2)


            with skill_col1:

                st.subheader(
                    "✅ Matched Required Skills"
                )


                if result["Matched Required"]:

                    for skill in result["Matched Required"]:

                        st.write(
                            f"✅ {skill}"
                        )

                else:

                    st.write(
                        "No required skills matched."
                    )


            with skill_col2:

                st.subheader(
                    "❌ Missing Required Skills"
                )


                if result["Missing Required"]:

                    for skill in result["Missing Required"]:

                        st.write(
                            f"❌ {skill}"
                        )

                else:

                    st.write(
                        "All required skills matched."
                    )


            st.divider()


            # ------------------------------------------------
            # PREFERRED SKILLS
            # ------------------------------------------------

            preferred_col1, preferred_col2 = st.columns(2)


            with preferred_col1:

                st.subheader(
                    "⭐ Matched Preferred Skills"
                )


                if result["Matched Preferred"]:

                    for skill in result["Matched Preferred"]:

                        st.write(
                            f"⭐ {skill}"
                        )

                else:

                    st.write(
                        "No preferred skills matched."
                    )


            with preferred_col2:

                st.subheader(
                    "⚠️ Missing Preferred Skills"
                )


                if result["Missing Preferred"]:

                    for skill in result["Missing Preferred"]:

                        st.write(
                            f"⚠️ {skill}"
                        )

                else:

                    st.write(
                        "All preferred skills matched."
                    )


            st.divider()


            # ------------------------------------------------
            # EXPERIENCE
            # ------------------------------------------------

            st.subheader(
                "💼 Experience"
            )


            if isinstance(
                result["Experience Details"],
                list
            ):

                for item in result["Experience Details"]:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    result["Experience Details"]
                )


            # ------------------------------------------------
            # EDUCATION
            # ------------------------------------------------

            st.subheader(
                "🎓 Education"
            )


            if isinstance(
                result["Education Details"],
                list
            ):

                for item in result["Education Details"]:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    result["Education Details"]
                )


            # ------------------------------------------------
            # CERTIFICATIONS
            # ------------------------------------------------

            st.subheader(
                "📜 Certifications"
            )


            if isinstance(
                result["Certifications"],
                list
            ):

                for item in result["Certifications"]:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    result["Certifications"]
                )


            # ------------------------------------------------
            # ACTIVITIES
            # ------------------------------------------------

            st.subheader(
                "🏅 Activities"
            )


            if isinstance(
                result["Activities"],
                list
            ):

                for item in result["Activities"]:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.write(
                    result["Activities"]
                )


    # ========================================================
    # COMPLETION
    # ========================================================

    st.divider()

    st.success(
        "🎉 Resume screening completed successfully!"
    )