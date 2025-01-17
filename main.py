import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os

# Directory containing known face images (modify this to your directory)
known_faces_dir = '/Users/atuljalal/Desktop/proj/Photo/'

# Initialize known faces and their names
known_faces = []
known_names = []

# Load known faces and names from images in the specified directory
def load_known_faces():
    for filename in os.listdir(known_faces_dir):
        if filename.lower().endswith(('.jpeg', '.jpg', '.png')):
            image = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                known_faces.append(face_encodings[0])  # Only store the first face encoding
                known_names.append(filename.split('.')[0])  # Use filename (without extension) as name
            else:
                print(f"No faces found in {filename}")

# Function to capture an image from the webcam
def capture_image():
    cam = cv2.VideoCapture(0)  # Open the default camera
    if not cam.isOpened():
        print("Error: Could not access the camera.")
        return None

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Display the frame in a window
        cv2.imshow('Press Space to Capture', frame)

        # Wait for the user to press the 'Space' key to capture the image
        if cv2.waitKey(1) & 0xFF == ord(' '):  # Space key
            break

    cam.release()
    cv2.destroyAllWindows()  # Close any OpenCV windows
    return frame if ret else None

# Function to recognize a face from the captured image
def recognize_face(captured_image):
    face_encodings = face_recognition.face_encodings(captured_image)
    if not face_encodings:
        print("No faces detected.")
        return None

    captured_encoding = face_encodings[0]  # Compare the first detected face

    # Compare the captured face with known faces
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]  # Return the name of the matched face
    return None

# Function to mark attendance in an Excel file
def mark_attendance(student_name, file='attendance.xlsx'):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    # Try to read the existing attendance file, if it doesn't exist, create a new one
    try:
        df = pd.read_excel(file)
    except FileNotFoundError:
        print("Attendance file not found, creating a new one.")
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    # Add a new record for the student
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)

    # Save the updated attendance to the file
    try:
        df.to_excel(file, index=False)
        print(f"Attendance marked for {student_name} at {current_time} on {current_date}")
    except Exception as e:
        print(f"Error saving the attendance file: {e}")

# Main function to run the system
def main():
    print("Loading known faces...")
    load_known_faces()  # Load known faces from the specified directory
    print(f"Loaded {len(known_faces)} known faces.")

    if not known_faces:
        print("No known faces loaded. Exiting...")
        return

    print("Press 'Space' to capture your image...")
    captured_image = capture_image()  # Capture an image from the webcam
    if captured_image is None:
        print("Failed to capture image. Exiting...")
        return

    # Recognize the face in the captured image
    student_name = recognize_face(captured_image)
    if student_name is None:
        print("Student not recognized!")
        return

    # Mark attendance for the recognized student
    mark_attendance(student_name)

if __name__ == "__main__":
    main()
