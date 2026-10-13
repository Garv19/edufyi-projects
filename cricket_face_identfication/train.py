import cv2
import os
import pickle
import numpy as np

# ==============================
# PATHS
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, "dataset", "indian players")
YUNET_MODEL = os.path.join(
    BASE_DIR, "models", "face_detection_yunet_2023mar.onnx"
)
SFACE_MODEL = os.path.join(
    BASE_DIR, "models", "face_recognition_sface_2021dec.onnx"
)

OUTPUT_FILE = os.path.join(BASE_DIR, "face_embeddings.pkl")


# ==============================
# LOAD MODELS
# ==============================

print("Loading YuNet face detector...")

face_detector = cv2.FaceDetectorYN.create(
    YUNET_MODEL,
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)

print("Loading SFace face recognizer...")

face_recognizer = cv2.FaceRecognizerSF.create(
    SFACE_MODEL,
    ""
)

print("Models loaded successfully.\n")


# ==============================
# FACE EMBEDDING FUNCTION
# ==============================

def get_face_embedding(image):
    """
    Detect the largest face in an image
    and generate its SFace embedding.
    """

    if image is None:
        return None

    height, width = image.shape[:2]

    # Tell YuNet the actual image size
    face_detector.setInputSize((width, height))

    _, faces = face_detector.detect(image)

    if faces is None or len(faces) == 0:
        return None

    # Select the largest detected face
    largest_face = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    # Align the face using SFace
    aligned_face = face_recognizer.alignCrop(
        image,
        largest_face
    )

    # Generate face feature/embedding
    feature = face_recognizer.feature(
        aligned_face
    )

    return feature


# ==============================
# TRAINING
# ==============================

embeddings = {}

total_images = 0
successful_images = 0
failed_images = 0


print("Starting training...\n")


# Get player folders
player_names = sorted(
    [
        folder
        for folder in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, folder))
    ]
)

print(f"Players found: {len(player_names)}")
print("-" * 50)


for player_name in player_names:

    player_folder = os.path.join(
        DATASET_DIR,
        player_name
    )

    player_embeddings = []

    image_files = [
        file
        for file in os.listdir(player_folder)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        )
    ]

    print(f"\n{player_name}")
    print(f"Images found: {len(image_files)}")

    for image_file in image_files:

        total_images += 1

        image_path = os.path.join(
            player_folder,
            image_file
        )

        image = cv2.imread(image_path)

        embedding = get_face_embedding(image)

        if embedding is None:

            failed_images += 1

            print(
                f"  SKIPPED: {image_file} "
                f"(no face detected)"
            )

            continue

        player_embeddings.append(
            embedding.flatten()
        )

        successful_images += 1

        print(
            f"  OK: {image_file}"
        )

    if player_embeddings:

        embeddings[player_name] = player_embeddings

        print(
            f"  → {len(player_embeddings)} "
            f"usable face embeddings"
        )

    else:

        print(
            "  → WARNING: No usable faces found!"
        )


# ==============================
# SAVE EMBEDDINGS
# ==============================

with open(
    OUTPUT_FILE,
    "wb"
) as file:

    pickle.dump(
        embeddings,
        file
    )


# ==============================
# FINAL SUMMARY
# ==============================

print("\n" + "=" * 50)

print("TRAINING COMPLETE")

print("=" * 50)

print(
    f"Players: {len(embeddings)}"
)

print(
    f"Total images: {total_images}"
)

print(
    f"Successful images: {successful_images}"
)

print(
    f"Skipped images: {failed_images}"
)

print(
    f"\nEmbeddings saved to:"
)

print(
    OUTPUT_FILE
)

print("=" * 50)