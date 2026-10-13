
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import re


# ==========================================
# 1. LOAD THE AI MODEL
# ==========================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# 2. READ JOB DESCRIPTION
# ==========================================

def read_job_description(file_path):
    """Read the job description from a text file."""

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ==========================================
# 3. CALCULATE REQUIRED SKILL MATCH
# ==========================================

def calculate_match(
    candidate_skills,
    required_skills
):
    """Compare candidate skills with required skills."""

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    required_set = {
        skill.lower()
        for skill in required_skills
    }

    matched_skills = candidate_set.intersection(
        required_set
    )

    missing_skills = required_set - candidate_set

    if len(required_set) == 0:
        match_score = 0
    else:
        match_score = (
            len(matched_skills)
            / len(required_set)
        ) * 100

    return (
        match_score,
        matched_skills,
        missing_skills
    )


# ==========================================
# 4. CALCULATE PREFERRED SKILL MATCH
# ==========================================

def calculate_preferred_match(
    candidate_skills,
    preferred_skills
):
    """Calculate preferred skill match."""

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    preferred_set = {
        skill.lower()
        for skill in preferred_skills
    }

    matched_preferred = candidate_set.intersection(
        preferred_set
    )

    missing_preferred = preferred_set - candidate_set

    if len(preferred_set) == 0:
        preferred_score = 0
    else:
        preferred_score = (
            len(matched_preferred)
            / len(preferred_set)
        ) * 100

    return (
        preferred_score,
        matched_preferred,
        missing_preferred
    )


# ==========================================
# 5. SEMANTIC AI MATCHING
# ==========================================

def semantic_similarity(
    resume_text,
    job_text
):
    """
    Compare the meaning of the resume
    and job description.
    """

    resume_embedding = model.encode(
        [resume_text]
    )

    job_embedding = model.encode(
        [job_text]
    )

    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    score = max(
        0.0,
        min(
            100.0,
            float(similarity) * 100
        )
    )

    return score


# ==========================================
# 6. EXTRACT YEARS FROM JOB DESCRIPTION
# ==========================================

def extract_required_years(job_text):
    """
    Extract required experience from the job
    description.

    Examples recognized:

    2 years
    2+ years
    3 years of experience
    minimum 2 years
    """

    patterns = [

        r"(\d+)\s*\+\s*years?",

        r"(\d+)\s+years?\s+of\s+experience",

        r"(\d+)\s+years?\s+experience",

        r"minimum\s+(\d+)\s+years?",

        r"at\s+least\s+(\d+)\s+years?",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            job_text,
            re.IGNORECASE
        )

        if match:

            return float(
                match.group(1)
            )

    # If the job description doesn't
    # specify experience, use entry-level
    # baseline.
    return 0.0


# ==========================================
# 7. PARSE EXPERIENCE DATE
# ==========================================

def parse_experience_period(experience_text):
    """
    Convert an experience period into
    start and end dates.

    Example:

    July’19 – Present

    becomes:

    start = July 2019
    end   = current date
    """

    text = experience_text.strip()

    # Normalize apostrophes
    text = text.replace(
        "′",
        "'"
    )

    text = text.replace(
        "’",
        "'"
    )

    # Remove text inside brackets
    text = re.sub(
        r"\([^)]*\)",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Match:
    # July'19 - Present
    # Feb'16 - June'19
    pattern = re.compile(
        r"""
        (?P<start_month>
            January|February|March|April|May|June|
            July|August|September|October|November|December|
            Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec
        )
        '
        (?P<start_year>\d{2,4})
        \s*
        [-–]
        \s*
        (?P<end>
            Present
            |
            (?P<end_month>
                January|February|March|April|May|June|
                July|August|September|October|November|December|
                Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec
            )
            '
            (?P<end_year>\d{2,4})
        )
        """,
        re.IGNORECASE | re.VERBOSE
    )

    match = pattern.search(text)

    if not match:
        return None

    start_month = match.group(
        "start_month"
    )

    start_year = int(
        match.group("start_year")
    )

    # Convert 2-digit year
    if start_year < 100:
        start_year += 2000

    start_month_number = month_to_number(
        start_month
    )

    start_date = datetime(
        start_year,
        start_month_number,
        1
    )

    # Present
    if match.group("end").lower() == "present":

        now = datetime.now()

        end_date = datetime(
            now.year,
            now.month,
            1
        )

    else:

        end_month = match.group(
            "end_month"
        )

        end_year = int(
            match.group("end_year")
        )

        if end_year < 100:
            end_year += 2000

        end_month_number = month_to_number(
            end_month
        )

        end_date = datetime(
            end_year,
            end_month_number,
            1
        )

    return (
        start_date,
        end_date
    )


# ==========================================
# 8. MONTH NAME TO NUMBER
# ==========================================

def month_to_number(month):

    months = {
        "jan": 1,
        "january": 1,

        "feb": 2,
        "february": 2,

        "mar": 3,
        "march": 3,

        "apr": 4,
        "april": 4,

        "may": 5,

        "jun": 6,
        "june": 6,

        "jul": 7,
        "july": 7,

        "aug": 8,
        "august": 8,

        "sep": 9,
        "september": 9,

        "oct": 10,
        "october": 10,

        "nov": 11,
        "november": 11,

        "dec": 12,
        "december": 12,
    }

    return months[
        month.lower()
    ]


# ==========================================
# 9. CALCULATE TOTAL EXPERIENCE
# ==========================================

def calculate_total_experience(
    candidate_experience
):
    """
    Calculate total professional experience
    in years from extracted date ranges.

    Overlapping periods are merged so that
    experience is not counted twice.
    """

    if not candidate_experience:
        return 0.0

    periods = []

    for item in candidate_experience:

        if not item:
            continue

        if item.lower() == "not found":
            continue

        parsed = parse_experience_period(
            item
        )

        if parsed:
            periods.append(parsed)

    if not periods:
        return 0.0

    # Sort by start date
    periods.sort(
        key=lambda x: x[0]
    )

    merged = []

    current_start, current_end = periods[0]

    for start, end in periods[1:]:

        # Overlapping or touching periods
        if start <= current_end:

            if end > current_end:
                current_end = end

        else:

            merged.append(
                (
                    current_start,
                    current_end
                )
            )

            current_start = start
            current_end = end

    merged.append(
        (
            current_start,
            current_end
        )
    )

    total_months = 0

    for start, end in merged:

        months = (
            (end.year - start.year) * 12
            + (end.month - start.month)
        )

        total_months += max(
            0,
            months
        )

    return total_months / 12


# ==========================================
# 10. AI EXPERIENCE RELEVANCE SCORE
# ==========================================

def calculate_experience_score(
    candidate_experience,
    job_text
):
    """
    Calculate experience score using:

    1. Actual years of experience
    2. Semantic relevance of experience

    If the job description specifies a required
    number of years, the years score is used.

    If no years are specified, semantic relevance
    is used more heavily.
    """

    if not candidate_experience:
        return 0.0

    valid_experience = [
        item
        for item in candidate_experience
        if item
        and item.lower() != "not found"
    ]

    if not valid_experience:
        return 0.0

    # --------------------------------------------------------
    # Calculate actual experience
    # --------------------------------------------------------

    total_years = calculate_total_experience(
        valid_experience
    )

    # --------------------------------------------------------
    # Calculate semantic relevance
    # --------------------------------------------------------

    experience_text = " ".join(
        valid_experience
    )

    experience_embedding = model.encode(
        [experience_text]
    )

    job_embedding = model.encode(
        [job_text]
    )

    similarity = cosine_similarity(
        experience_embedding,
        job_embedding
    )[0][0]

    semantic_score = max(
        0.0,
        min(
            100.0,
            float(similarity) * 100
        )
    )

    # --------------------------------------------------------
    # Extract required years
    # --------------------------------------------------------

    required_years = extract_required_years(
        job_text
    )

    # --------------------------------------------------------
    # Calculate years score
    # --------------------------------------------------------

    if required_years > 0:

        years_score = min(
            100.0,
            (
                total_years
                / required_years
            ) * 100
        )

        # Combine:
        # 70% actual experience
        # 30% semantic relevance

        final_score = (
            years_score * 0.70
            + semantic_score * 0.30
        )

    else:

        # No explicit experience requirement
        # in JD.

        # Use actual experience as a supporting
        # factor without allowing it to dominate.

        experience_amount_score = min(
            100.0,
            total_years * 20
        )

        final_score = (
            experience_amount_score * 0.40
            + semantic_score * 0.60
        )

    return max(
        0.0,
        min(
            100.0,
            final_score
        )
    )


# ==========================================
# 11. AI EDUCATION RELEVANCE SCORE
# ==========================================

def calculate_education_score(
    candidate_education,
    job_text
):
    """
    Calculate how relevant the candidate's
    education is to the job description.
    """

    if not candidate_education:
        return 0.0

    valid_education = [
        item
        for item in candidate_education
        if item.lower() != "not found"
    ]

    if not valid_education:
        return 0.0

    education_text = " ".join(
        valid_education
    )

    education_embedding = model.encode(
        [education_text]
    )

    job_embedding = model.encode(
        [job_text]
    )

    similarity = cosine_similarity(
        education_embedding,
        job_embedding
    )[0][0]

    score = max(
        0.0,
        min(
            100.0,
            float(similarity) * 100
        )
    )

    return score