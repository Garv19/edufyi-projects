import streamlit as st
import cv2
import os
import pickle
import numpy as np
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# NLP KNOWLEDGE BASE
# ============================================================

player_info = {
    "Virat Kohli": """
    Virat Kohli is an Indian cricketer and a right-handed top-order batter.
    He is known for his batting, consistency, fitness and leadership.
    """,

    "Rohit Sharma": """
    Rohit Sharma is an Indian cricketer and a right-handed opening batter.
    He is known for his powerful batting and leadership.
    """,

    "KL Rahul": """
    KL Rahul is an Indian cricketer and a right-handed batter.
    He can play as a top-order batter and wicketkeeper.
    """,

    "Shubman Gill": """
    Shubman Gill is an Indian cricketer and a right-handed top-order batter.
    He is known for his technically strong batting.
    """,

    "Rishabh Pant": """
    Rishabh Pant is an Indian cricketer, left-handed batter and wicketkeeper.
    He is known for his aggressive batting style.
    """,

    "Hardik Pandya": """
    Hardik Pandya is an Indian cricketer and an all-rounder.
    He is a right-handed batter and a right-arm fast-medium bowler.
    """,

    "Ravindra Jadeja": """
    Ravindra Jadeja is an Indian cricketer and an all-rounder.
    He is a left-handed batter and a left-arm orthodox spin bowler.
    """,

    "Jasprit Bumrah": """
    Jasprit Bumrah is an Indian cricketer and a right-arm fast bowler.
    He is known for his pace, accuracy and unusual bowling action.
    """,

    "Mohammed Siraj": """
    Mohammed Siraj is an Indian cricketer and a right-arm fast bowler.
    He is known for his pace and ability to generate movement.
    """,

    "Suryakumar Yadav": """
    Suryakumar Yadav is an Indian cricketer and a right-handed batter.
    He is known for his innovative and aggressive batting style.
    """,

    "Kuldeep Yadav": """
    Kuldeep Yadav is an Indian cricketer and a left-arm wrist-spin bowler.
    He is known for his variations and ability to take wickets.
    """
}

# ============================================================
# NLP QUESTION ANSWER FUNCTION
# ============================================================

def answer_question(question):

    questions = list(player_info.values())
    player_names = list(player_info.keys())

    vectorizer = TfidfVectorizer(stop_words="english")

    tfidf_matrix = vectorizer.fit_transform(questions)
    question_vector = vectorizer.transform([question])

    similarity_scores = cosine_similarity(
        question_vector,
        tfidf_matrix
    )[0]

    best_index = np.argmax(similarity_scores)
    best_score = similarity_scores[best_index]

    if best_score < 0.10:
        return (
            "Sorry, I can only answer questions "
            "about the 11 selected Indian cricket players."
        )

    player = player_names[best_index]

    return f"**{player}**\n\n{player_info[player]}"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

YUNET_MODEL = os.path.join(
    BASE_DIR,
    "models",
    "face_detection_yunet_2023mar.onnx"
)

SFACE_MODEL = os.path.join(
    BASE_DIR,
    "models",
    "face_recognition_sface_2021dec.onnx"
)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "face_embeddings.pkl"
)


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def load_models():

    detector = cv2.FaceDetectorYN.create(
        YUNET_MODEL,
        "",
        (320, 320),
        0.9,
        0.3,
        5000
    )

    recognizer = cv2.FaceRecognizerSF.create(
        SFACE_MODEL,
        ""
    )

    return detector, recognizer


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

@st.cache_resource
def load_embeddings():

    with open(EMBEDDINGS_FILE, "rb") as file:
        return pickle.load(file)


face_detector, face_recognizer = load_models()
embeddings = load_embeddings()


# ============================================================
# PAGE DESIGN
# ============================================================

st.set_page_config(
    page_title="Indian Cricket Face Identification",
    page_icon="🏏",
    layout="centered"
)

st.title("🏏 Indian Cricket Team")
st.subheader("Face Identification System")

st.write(
    "Upload a photo of an Indian cricket player "
    "and the system will identify the player."
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a player's image",
    type=["jpg", "jpeg", "png"]
)


# ============================================================
# PROCESS IMAGE
# ============================================================

if uploaded_file is not None:

    # Read uploaded image
    pil_image = Image.open(uploaded_file).convert("RGB")

    image = np.array(pil_image)

    # Convert RGB → BGR for OpenCV
    image_bgr = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    st.image(
        pil_image,
        caption="Uploaded Image",
        use_container_width=True
    )

    # --------------------------------------------------------
    # FACE DETECTION
    # --------------------------------------------------------

    height, width = image_bgr.shape[:2]

    face_detector.setInputSize(
        (width, height)
    )

    _, faces = face_detector.detect(
        image_bgr
    )

    if faces is None or len(faces) == 0:

        st.error(
            "❌ No face detected in the image."
        )

    else:

        # Select largest face
        face = max(
            faces,
            key=lambda f: f[2] * f[3]
        )

        # ----------------------------------------------------
        # CREATE FACE EMBEDDING
        # ----------------------------------------------------

        aligned_face = face_recognizer.alignCrop(
            image_bgr,
            face
        )

        test_feature = face_recognizer.feature(
            aligned_face
        )

        # ----------------------------------------------------
        # COMPARE WITH ALL PLAYERS
        # ----------------------------------------------------

        best_player = None
        best_score = -1

        player_scores = {}

        for player_name, player_embeddings in embeddings.items():

            scores = []

            for stored_feature in player_embeddings:

                stored_feature = np.asarray(
                    stored_feature,
                    dtype=np.float32
                ).reshape(1, -1)

                score = face_recognizer.match(
                    test_feature,
                    stored_feature,
                    cv2.FaceRecognizerSF_FR_COSINE
                )

                scores.append(
                    float(score)
                )

            player_score = max(scores)

            player_scores[player_name] = player_score

            if player_score > best_score:

                best_score = player_score
                best_player = player_name

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        st.success(
            f"🏏 Identified Player: {best_player}"
        )

        st.metric(
            "Similarity Score",
            f"{best_score:.4f}"
        )

        # ----------------------------------------------------
        # SHOW OTHER SCORES
        # ----------------------------------------------------

        st.subheader("Recognition Scores")

        sorted_scores = sorted(
            player_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for player, score in sorted_scores:

            st.write(
                f"**{player}** — {score:.4f}"
            )
            
# ============================================================
# CRICKET PLAYER NLP ASSISTANT
# ============================================================

st.markdown("---")

st.header("💬 Cricket Player Assistant")

question = st.text_input(
    "Ask something about the selected Indian cricket players:"
)

if question:
    answer = answer_question(question)
    st.markdown(answer)