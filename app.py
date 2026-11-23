
from flask import Flask, render_template, request, send_from_directory
import os
import uuid
import sqlite3

from werkzeug.utils import secure_filename
from PIL import Image

from predict import predict_disease
from disease_info import DISEASE_INFO
from report import generate_report
from database import create_tables, get_connection


app = Flask(__name__)

# Application settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "static", "reports")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

CONFIDENCE_THRESHOLD = 50.0

# Create required folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Initialize database tables automatically on startup
create_tables()


# Check allowed image extensions
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Save uploaded image in database
def save_upload_history(filename):

    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO detection_history
            (user_id, image_filename, disease_name, confidence)
            VALUES (?, ?, ?, ?)
        """, (None, filename, None, None))

        connection.commit()

    finally:
        connection.close()


# Update AI prediction in database
def update_prediction_history(filename, disease_name, confidence):

    connection = get_connection()

    try:
        connection.execute("""
            UPDATE detection_history
            SET disease_name = ?, confidence = ?
            WHERE image_filename = ?
        """, (disease_name, confidence, filename))

        connection.commit()

    finally:
        connection.close()


# Get detection history
def get_history():

    connection = get_connection()

    try:
        history = connection.execute("""
            SELECT *
            FROM detection_history
            ORDER BY detected_at DESC
        """).fetchall()

        return history

    finally:
        connection.close()


# Calculate dashboard statistics
def get_dashboard_stats():

    connection = get_connection()

    try:
        total_uploads = connection.execute("""
            SELECT COUNT(*)
            FROM detection_history
        """).fetchone()[0]

        diseases_detected = connection.execute("""
            SELECT COUNT(*)
            FROM detection_history
            WHERE disease_name IS NOT NULL
            AND disease_name != 'Uncertain prediction'
        """).fetchone()[0]

        pending_predictions = connection.execute("""
            SELECT COUNT(*)
            FROM detection_history
            WHERE disease_name IS NULL
        """).fetchone()[0]

        uncertain_predictions = connection.execute("""
            SELECT COUNT(*)
            FROM detection_history
            WHERE disease_name = 'Uncertain prediction'
        """).fetchone()[0]

        return {
            "total_uploads": total_uploads,
            "diseases_detected": diseases_detected,
            "pending_predictions": pending_predictions,
            "uncertain_predictions": uncertain_predictions
        }

    finally:
        connection.close()


# Home page
@app.route("/", methods=["GET", "POST"])
def home():

    uploaded_image = None
    disease = None
    confidence = None
    error = None
    report_url = None

    if request.method == "POST":

        image = request.files.get("leaf_image")

        if not image or image.filename == "":
            error = "Please select a plant leaf image."

        elif not allowed_file(image.filename):
            error = "Please upload JPG, JPEG or PNG images."

        else:

            original_name = secure_filename(image.filename)

            extension = original_name.rsplit(".", 1)[1].lower()

            unique_filename = f"{uuid.uuid4().hex}.{extension}"

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_filename
            )

            try:

                # Save uploaded image
                image.save(image_path)

                # Validate actual image contents
                with Image.open(image_path) as uploaded_file:
                    uploaded_file.verify()

                # Save upload history
                save_upload_history(unique_filename)

                uploaded_image = (
                    "/static/uploads/" + unique_filename
                )

                # Run AI prediction
                predicted_label, confidence = predict_disease(image_path)

                # Check prediction confidence
                if confidence >= CONFIDENCE_THRESHOLD:

                    disease = DISEASE_INFO.get(
                        predicted_label,
                        {
                            "name": predicted_label.replace("_", " "),
                            "symptoms": (
                                "Disease information is not available."
                            ),
                            "advice": (
                                "Consult an agricultural expert for guidance."
                            )
                        }
                    )

                    # Save confident prediction
                    update_prediction_history(
                        unique_filename,
                        predicted_label,
                        confidence
                    )

                else:

                    # Handle uncertain prediction
                    disease = {
                        "name": "Unable to Identify Disease Confidently",
                        "symptoms": (
                            "The AI model is not sufficiently confident "
                            "about this prediction."
                        ),
                        "advice": (
                            "Please upload a clear plant leaf image "
                            "with good lighting, or consult an "
                            "agricultural expert."
                        )
                    }

                    # Save uncertain result
                    update_prediction_history(
                        unique_filename,
                        "Uncertain prediction",
                        confidence
                    )

                # Generate PDF report
                report_filename = generate_report(
                    image_path,
                    disease,
                    confidence
                )

                # Create PDF download URL
                report_url = "/download-report/" + report_filename

            except Exception as e:

                error = (
                    "Unable to analyze this image or generate its report. "
                    "Please try again."
                )

                print("CropCare error:", str(e))

                # Remove uploaded image if processing fails
                if os.path.exists(image_path):
                    os.remove(image_path)

                uploaded_image = None
                report_url = None

    # Get latest history and dashboard statistics
    history = get_history()
    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        uploaded_image=uploaded_image,
        disease=disease,
        confidence=confidence,
        error=error,
        history=history,
        stats=stats,
        report_url=report_url
    )


# Download PDF report
@app.route("/download-report/<filename>")
def download_report(filename):

    return send_from_directory(
        app.config["REPORT_FOLDER"],
        filename,
        as_attachment=True
    )


# Run application locally
if __name__ == "__main__":
    app.run(debug=True)






