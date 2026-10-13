import cv2
import os
import pickle
import numpy as np

# ==============================
# PATHS
# ==============================

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


# ==============================
# LOAD MODELS
# ==============================

face_detector = cv2.FaceDetectorYN.create(
    YUNET_MODEL,
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)

face_recognizer = cv2.FaceRecognizerSF.create(
    SFACE_MODEL,
    ""
)


# ==============================
# LOAD TRAINED EMBEDDINGS
# ==============================

with open(EMBEDDINGS_FILE, "rb") as file:
    embeddings = pickle.load(file)

print("Loaded players:")

for player in embeddings:
    print(
        f"  {player}: "
        f"{len(embeddings[player])} embeddings"
    )


# ==============================
# SELECT TEST IMAGE
# ==============================

image_path = input(
    "\nEnter the full path of the test image: "
).strip().strip('"')


image = cv2.imread(image_path)

if image is None:
    print("\nERROR: Could not read the image.")
    exit()


# ==============================
# DETECT FACE
# ==============================

height, width = image.shape[:2]

face_detector.setInputSize(
    (width, height)
)

_, faces = face_detector.detect(image)


if faces is None or len(faces) == 0:

    print("\nNo face detected in the image.")
    exit()


print(
    f"\nFaces detected: {len(faces)}"
)


# ==============================
# SELECT LARGEST FACE
# ==============================

face = max(
    faces,
    key=lambda f: f[2] * f[3]
)


# ==============================
# CREATE TEST EMBEDDING
# ==============================

aligned_face = face_recognizer.alignCrop(
    image,
    face
)

test_feature = face_recognizer.feature(
    aligned_face
)


# ==============================
# COMPARE WITH ALL PLAYERS
# ==============================

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

        scores.append(float(score))


    # Use the best matching training image
    player_score = max(scores)

    player_scores[player_name] = player_score

    if player_score > best_score:

        best_score = player_score
        best_player = player_name


# ==============================
# DISPLAY RESULTS
# ==============================

print("\n" + "=" * 50)

print("FACE IDENTIFICATION RESULT")

print("=" * 50)

print(
    f"Predicted Player: {best_player}"
)

print(
    f"Similarity Score: {best_score:.4f}"
)

print("\nAll Player Scores:")

sorted_scores = sorted(
    player_scores.items(),
    key=lambda x: x[1],
    reverse=True
)

for player, score in sorted_scores:

    print(
        f"{player:25s} "
        f"{score:.4f}"
    )

print("=" * 50)