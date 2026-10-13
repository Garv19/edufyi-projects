import re


# ============================================================
# SKILL DATABASE
# ============================================================

SKILLS = [
    "Python",
    "SQL",
    "Linux",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Natural Language Processing",
    "Data Analysis",
    "Data Science",
    "Artificial Intelligence",
    "TF-IDF",
    "Naive Bayes",
    "Logistic Regression",
    "Random Forest",
    "XGBoost",
    "TensorFlow",
    "Keras",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Jupyter Notebook",
    "PyGObject",
    "IAM",
    "IAM Fundamentals",
    "Access Control",
    "Cybersecurity",
    "AWS",
    "Azure",
    "Git",
    "GitHub",
    "Statistics",
    "Power BI"
]


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):
    """
    Find known skills in the given text.
    """

    if not text:
        return []

    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:

        skill_lower = skill.lower()

        if skill_lower in text_lower:

            found_skills.append(skill)

    return found_skills