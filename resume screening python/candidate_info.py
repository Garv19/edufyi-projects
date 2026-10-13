import re
from resume_parser import extract_text


# ============================================================
# BASIC TEXT CLEANING
# ============================================================

def get_clean_lines(text):
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return lines


def normalize_heading(line):
    return re.sub(r"[^A-Z]", "", line.upper())


def find_section(lines, possible_headings):
    normalized_headings = [
        normalize_heading(h)
        for h in possible_headings
    ]

    for i, line in enumerate(lines):
        normalized = normalize_heading(line)

        if normalized in normalized_headings:
            return i

    return -1


def extract_section(lines, possible_headings, stop_headings):
    start = find_section(
        lines,
        possible_headings
    )

    if start == -1:
        return []

    section = []

    normalized_stop_headings = [
        normalize_heading(h)
        for h in stop_headings
    ]

    for line in lines[start + 1:]:

        normalized = normalize_heading(line)

        if normalized in normalized_stop_headings:
            break

        section.append(line)

    return section


def remove_duplicates(items):
    result = []

    for item in items:

        if item not in result:
            result.append(item)

    return result


# ============================================================
# NAME
# ============================================================

def extract_name(text):

    lines = get_clean_lines(text)

    if not lines:
        return "Not Found"

    first_line = lines[0]

    if "Email:" in first_line:
        first_line = first_line.split(
            "Email:"
        )[0].strip()

    if first_line:
        return first_line

    return "Not Found"


# ============================================================
# DATE CLEANING
# ============================================================

def clean_date_spacing(text):
    """
    Fix PDF extraction problems such as:

    July’1 9  -> July’19
    June’1 9  -> June’19
    """

    # Normalize apostrophe characters
    text = text.replace("′", "’")
    text = text.replace("'", "’")

    # --------------------------------------------------------
    # July’1 9 -> July’19
    # June’1 9 -> June’19
    # --------------------------------------------------------
    text = re.sub(
        r"([A-Za-z]+)\s*’\s*(\d)\s+(\d)",
        r"\1’\2\3",
        text
    )

    # --------------------------------------------------------
    # Handle cases where apostrophe disappears completely
    # Example:
    # July 1 9 -> July’19
    # --------------------------------------------------------
    text = re.sub(
        r"\b"
        r"(July|June|May|April|March|February|January|"
        r"August|September|October|November|December|"
        r"Jul|Jun|Apr|Mar|Feb|Jan|Aug|Sep|Oct|Nov|Dec)"
        r"\s+(\d)\s+(\d)"
        r"\b",
        r"\1’\2\3",
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def clean_experience_line(line):

    line = clean_date_spacing(line)

    line = re.sub(
        r"\s+",
        " ",
        line
    ).strip()

    return line


# ============================================================
# EXPERIENCE DATE PATTERNS
# ============================================================

EXPERIENCE_DATE_PATTERN = re.compile(
    r"""
    (
        (?:
            Jan(?:uary)?|
            Feb(?:ruary)?|
            Mar(?:ch)?|
            Apr(?:il)?|
            May|
            Jun(?:e)?|
            Jul(?:y)?|
            Aug(?:ust)?|
            Sep(?:tember)?|
            Oct(?:ober)?|
            Nov(?:ember)?|
            Dec(?:ember)?
        )
        [’']?\s*\d{2,4}
        \s*
        [-–]
        \s*
        (?:
            Present|
            Jan(?:uary)?|
            Feb(?:ruary)?|
            Mar(?:ch)?|
            Apr(?:il)?|
            May|
            Jun(?:e)?|
            Jul(?:y)?|
            Aug(?:ust)?|
            Sep(?:tember)?|
            Oct(?:ober)?|
            Nov(?:ember)?|
            Dec(?:ember)?
        )
        [’']?\s*\d{0,4}
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


RICHA_DATE_PATTERN = re.compile(
    r"""
    (
        (?:
            Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec
        )
        [a-z]*
        [’']?\s*\d{1,2}
        \s*
        [-–]
        \s*
        (?:
            Present|
            Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec
        )
        [a-z]*
        [’']?\s*\d{1,2}
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


# ============================================================
# JOB KEYWORDS
# ============================================================

JOB_KEYWORDS = [
    "intern",
    "engineer",
    "developer",
    "consultant",
    "scientist",
    "manager",
    "analyst",
    "lead",
    "practitioner",
    "director",
    "administrator",
    "architect",
]


def looks_like_job_line(line):

    lower = line.lower()

    return (
        any(
            keyword in lower
            for keyword in JOB_KEYWORDS
        )
        and bool(
            EXPERIENCE_DATE_PATTERN.search(line)
            or RICHA_DATE_PATTERN.search(line)
        )
    )


def looks_like_description(line):

    lower = line.lower()

    description_words = [
        "responsible",
        "developed",
        "develop",
        "worked",
        "built",
        "managed",
        "created",
        "designed",
        "experience",
        "using",
        "working",
        "leading",
        "collaborated",
    ]

    return any(
        word in lower
        for word in description_words
    )


# ============================================================
# RICHA EXPERIENCE
# ============================================================

def extract_richa_experience(lines):

    experience = []

    for line in lines:

        line = clean_experience_line(line)

        match = RICHA_DATE_PATTERN.search(
            line
        )

        if match:

            date_text = match.group(1)

            date_text = clean_date_spacing(
                date_text
            )

            date_text = re.sub(
                r"\s+",
                " ",
                date_text
            ).strip()

            experience.append(
                date_text
            )

    return remove_duplicates(
        experience
    )


# ============================================================
# STANDARD EXPERIENCE
# ============================================================

def extract_standard_experience(lines):

    experience = []

    for line in lines:

        line = clean_experience_line(line)

        if looks_like_job_line(line):

            match = (
                EXPERIENCE_DATE_PATTERN.search(line)
                or RICHA_DATE_PATTERN.search(line)
            )

            if match:

                date_text = match.group(1)

                date_text = clean_date_spacing(
                    date_text
                )

                date_text = re.sub(
                    r"\s+",
                    " ",
                    date_text
                ).strip()

                experience.append(
                    line
                )

    return remove_duplicates(
        experience
    )


# ============================================================
# MAIN EXPERIENCE FUNCTION
# ============================================================

def extract_experience(text):

    lines = get_clean_lines(text)

    # Try Richa-style dates first
    richa_experience = extract_richa_experience(
        lines
    )

    if richa_experience:
        return richa_experience

    # Otherwise use standard parser
    return extract_standard_experience(
        lines
    )


# ============================================================
# COMPANIES
# ============================================================

def extract_companies(text):

    lines = get_clean_lines(text)

    companies = []

    for line in lines:

        # Richa-style:
        # Company as Role
        if " as " in line.lower():

            parts = re.split(
                r"\s+as\s+",
                line,
                flags=re.IGNORECASE
            )

            if len(parts) >= 2:

                company_part = parts[0].strip()

                if company_part:
                    companies.append(
                        company_part
                    )

        # Garv / Bhavesh style
        elif (
            "LLP" in line
            or "Ltd" in line
            or "Limited" in line
            or "Technologies" in line
            or "Infosys" in line
            or "Standard Chartered" in line
            or "RBS" in line
            or "Corporation" in line
        ):

            if not looks_like_description(line):
                companies.append(line)

    cleaned = []

    for company in companies:

        company = re.sub(
            r"\s+",
            " ",
            company
        ).strip()

        # Remove trailing dates
        company = re.sub(
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*[’']?\s*\d{2,4}.*$",
            "",
            company,
            flags=re.IGNORECASE
        ).strip()

        if company:
            cleaned.append(
                company
            )

    return remove_duplicates(
        cleaned
    )


# ============================================================
# EXPERIENCE DURATION
# ============================================================

def extract_experience_duration(text):

    lines = get_clean_lines(text)

    durations = []

    for line in lines:

        line = clean_experience_line(line)

        # Richa-style
        match = RICHA_DATE_PATTERN.search(
            line
        )

        if match:

            date_text = match.group(1)

            date_text = clean_date_spacing(
                date_text
            )

            date_text = re.sub(
                r"\s+",
                " ",
                date_text
            ).strip()

            durations.append(
                date_text
            )

            continue

        # Standard style
        match = EXPERIENCE_DATE_PATTERN.search(
            line
        )

        if match:

            date_text = match.group(1)

            date_text = clean_date_spacing(
                date_text
            )

            date_text = re.sub(
                r"\s+",
                " ",
                date_text
            ).strip()

            durations.append(
                date_text
            )

    return remove_duplicates(
        durations
    )


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text):

    lines = get_clean_lines(text)

    education_headings = [
        "EDUCATION",
        "EDUCATIONAL QUALIFICATIONS",
    ]

    stop_headings = [
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "WORKEXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "CERTIFICATIONS",
        "CERTIFICATION",
        "SKILLS",
        "TECHNICAL SKILLS",
        "ACTIVITIES",
        "EXTRA-CURRICULAR ACTIVITIES",
        "PROJECTS",
        "ORGANIZATIONAL SCAN",
    ]

    education = extract_section(
        lines,
        education_headings,
        stop_headings
    )

    cleaned = []

    for line in education:

        line = line.strip()

        if not line:
            continue

        if "linkedin" in line.lower():
            continue

        if line.lower() == "page":
            continue

        cleaned.append(line)

    if cleaned:
        return remove_duplicates(
            cleaned
        )

    return ["Not Found"]


# ============================================================
# CERTIFICATIONS
# ============================================================

def clean_certification_text(line):

    # Remove [See the Certificate]
    line = re.sub(
        r"\[\s*See\s*the\s*Certificate\s*\]",
        "",
        line,
        flags=re.IGNORECASE
    )

    line = re.sub(
        r"\s+",
        " ",
        line
    ).strip()

    return line


def extract_bhavesh_certifications(lines):

    certifications = []

    for line in lines:

        lower = line.lower()

        if (
            "microsoftcertified" in lower
            or "googlecertified" in lower
            or "2020certification" in lower
        ):

            line = clean_certification_text(
                line
            )

            certifications.append(
                line
            )

        elif certifications:

            if (
                "writing" in lower
                or "technical blog writer" in lower
                or "endtoend" in lower
            ):
                break

    return remove_duplicates(
        certifications
    )


def extract_certifications(text):

    lines = get_clean_lines(text)

    # Bhavesh-style certifications
    bhavesh = extract_bhavesh_certifications(
        lines
    )

    if bhavesh:
        return bhavesh

    certification_headings = [
        "CERTIFICATIONS",
        "CERTIFICATION",
        "CERTIFICATIONS & TRAINING",
        "CERTIFICATION & TRAINING",
    ]

    stop_headings = [
        "EDUCATION",
        "EDUCATIONAL QUALIFICATIONS",
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "PROJECTS",
        "ACTIVITIES",
        "EXTRA-CURRICULAR ACTIVITIES",
        "SKILLS",
        "TECHNICAL SKILLS",
    ]

    certifications = extract_section(
        lines,
        certification_headings,
        stop_headings
    )

    cleaned = []

    for line in certifications:

        if looks_like_description(line):
            continue

        line = clean_certification_text(
            line
        )

        if line:
            cleaned.append(line)

    if cleaned:
        return remove_duplicates(
            cleaned
        )

    return ["Not Found"]


# ============================================================
# ACTIVITIES
# ============================================================

def extract_activities(text):

    lines = get_clean_lines(text)

    activity_headings = [
        "ACTIVITIES",
        "EXTRA-CURRICULAR ACTIVITIES",
        "EXTRACURRICULAR ACTIVITIES",
    ]

    stop_headings = [
        "EDUCATION",
        "EDUCATIONAL QUALIFICATIONS",
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "CERTIFICATIONS",
        "CERTIFICATION",
        "SKILLS",
        "TECHNICAL SKILLS",
        "PROJECTS",
    ]

    activities = extract_section(
        lines,
        activity_headings,
        stop_headings
    )

    cleaned = []

    for line in activities:

        if line.strip():
            cleaned.append(
                line.strip()
            )

    if cleaned:
        return remove_duplicates(
            cleaned
        )

    return ["Not Found"]


# ============================================================
# COMPLETE CANDIDATE INFORMATION
# ============================================================

def extract_candidate_info(text):

    candidate_info = {

        "Name": extract_name(text),

        "Education": extract_education(text),

        "Experience": extract_experience(text),

        "Companies": extract_companies(text),

        "Experience Duration": extract_experience_duration(text),

        "Certifications": extract_certifications(text),

        "Activities": extract_activities(text),
    }

    return candidate_info


# ============================================================
# PRINT FUNCTION
# ============================================================

def print_candidate_info(candidate_info):

    print("=" * 30)
    print("CANDIDATE INFORMATION")
    print("=" * 30)

    print()

    print("Name:", candidate_info["Name"])

    print()

    print("Education:")

    for item in candidate_info["Education"]:
        print(" -", item)

    print()

    print("Experience:")

    for item in candidate_info["Experience"]:
        print(" -", item)

    print()

    print("Companies:")

    for item in candidate_info["Companies"]:
        print(" -", item)

    print()

    print("Experience Duration:")

    for item in candidate_info["Experience Duration"]:
        print(" -", item)

    print()

    print("Certifications:")

    for item in candidate_info["Certifications"]:
        print(" -", item)

    print()

    print("Activities:")

    for item in candidate_info["Activities"]:
        print(" -", item)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    resume_path = "resumes/candidate3.pdf"

    # IMPORTANT:
    # Your resume_parser.py uses extract_text()
    resume_text = extract_text(
        resume_path
    )

    candidate_info = extract_candidate_info(
        resume_text
    )

    print_candidate_info(
        candidate_info
    )

