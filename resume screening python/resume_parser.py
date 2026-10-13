import PyPDF2


def extract_text(pdf_path):
    """
    Extract text from a PDF resume.
    """

    text = ""

    with open(pdf_path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


if __name__ == "__main__":

    resume_path = "resumes/candidate1.pdf"

    text = extract_text(resume_path)

    print("==============================")
    print("EXTRACTED RESUME TEXT")
    print("==============================")
    print()

    print(text)