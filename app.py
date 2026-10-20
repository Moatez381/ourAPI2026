import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------

# Set JWT_SECRET_KEY in your environment for real use.
# The fallback is for local demos only.
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-only-secret-change-me-and-make-it-long-123456"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)


# ---------------- CLASSES ----------------

class Student:
    def __init__(self, ID_S, FN, LN, DMjr, Level):
        self.ID_S = ID_S
        self.FN = FN
        self.LN = LN
        self.DMjr = DMjr
        self.Level = Level

    def to_dict(self):
        return {
            "ID_S": self.ID_S,
            "FN": self.FN,
            "LN": self.LN,
            "DMjr": self.DMjr,
            "Level": self.Level,
        }


class Report:
    def __init__(self, ID_R, Title, Type, K1, K2, K3, Release_Date):
        self.ID_R = ID_R
        self.Title = Title
        self.Type = Type
        self.K1 = K1
        self.K2 = K2
        self.K3 = K3
        self.Release_Date = Release_Date

    def to_dict(self):
        return {
            "ID_R": self.ID_R,
            "Title": self.Title,
            "Type": self.Type,
            "K1": self.K1,
            "K2": self.K2,
            "K3": self.K3,
            "Release_Date": self.Release_Date,
        }


# ---------------- TWO LISTS ----------------

students = [
    Student(1, "Ali", "Ben Salem", 1, 3),
    Student(2, "Sara", "Trabelsi", 0, 2),
    Student(3, "Moatez", "Bedoui", 3, 1),
]

reports = [
    Report(1, "Business Analysis", "Academic", "A", "B", "C", "2026-10-19"),
    Report(2, "Information Systems", "Academic", "B", "A", "C", "2026-10-20"),
    Report(3, "Business Analysis", "Academic", "C", "B", "A", "2026-10-19"),
]


# ---------------- HELPERS ----------------

def read_json():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, (
            jsonify({"error": "A valid JSON object is required"}), 400
        )

    return data, None


def find_student(student_id):
    return next((s for s in students if s.ID_S == student_id), None)


def find_report(report_id):
    return next((r for r in reports if r.ID_R == report_id), None)


def is_strict_int(value):
    # bool is a subclass of int in Python, so exclude it explicitly
    return type(value) is int


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_student_fields(FN, LN, DMjr, Level):
    """Return an error response tuple, or None if everything is valid."""
    if not is_text(FN) or not is_text(LN):
        return jsonify({"error": "FN and LN must be non-empty strings"}), 400

    if not is_strict_int(DMjr) or DMjr not in (0, 1):
        return jsonify({"error": "DMjr must be 0 or 1"}), 400

    if not is_strict_int(Level) or Level not in (1, 2, 3, 4):
        return jsonify({"error": "Level must be 1, 2, 3 or 4"}), 400

    return None


def validate_report_fields(Title, Type, K1, K2, K3, Release_Date):
    """Return an error response tuple, or None if everything is valid."""
    if not is_text(Title) or not is_text(Type):
        return jsonify({"error": "Title and Type are required"}), 400

    if not all(is_text(k) for k in (K1, K2, K3)):
        return jsonify(
            {"error": "K1, K2 and K3 must be non-empty strings"}
        ), 400

    if not valid_date(Release_Date):
        return jsonify(
            {"error": "Release_Date must use YYYY-MM-DD format"}
        ), 400

    return None


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


@jwt.unauthorized_loader
def missing_token(error):
    return jsonify({"error": "Access token required"}), 401


@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({"error": "Invalid token"}), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    if jwt_payload.get("type") == "refresh":
        return jsonify({
            "error": "Refresh token expired",
            "message": "Please log in again with POST /login."
        }), 401

    return jsonify({
        "error": "Access token expired",
        "message": "Use POST /refresh with your refresh token."
    }), 401


# ---------------- HOME ----------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API is running",
        "endpoints": {
            "auth": ["POST /login", "POST /refresh"],
            "students (token required)": [
                "GET /students", "GET /students/<id>", "POST /students",
                "PUT /students/<id>", "DELETE /students/<id>",
            ],
            "reports (public)": [
                "GET /reports", "GET /reports/<id>", "POST /reports",
                "PUT /reports/<id>", "DELETE /reports/<id>",
            ],
        },
    }), 200


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():
    data, error = read_json()

    if error:
        return error

    # Demo credentials only
    if (data.get("username") != "admin"
            or data.get("password") != "admin123"):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity="admin")
    refresh_token = create_refresh_token(identity="admin")

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 300
    }), 200


# ---------------- REFRESH TOKEN ----------------

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    new_token = create_access_token(identity=get_jwt_identity())

    return jsonify({
        "access_token": new_token,
        "expires_in": 300
    }), 200


# ==================================================
#                     STUDENTS
#              (ALL ROUTES REQUIRE A TOKEN)
# ==================================================

@app.route("/students", methods=["GET"])
@jwt_required()
def get_all_students():
    return jsonify([s.to_dict() for s in students]), 200


@app.route("/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student.to_dict()), 200


@app.route("/students", methods=["POST"])
@jwt_required()  # was missing before: POST was the only unprotected student route
def post_student():
    data, error = read_json()

    if error:
        return error

    required = ["ID_S", "FN", "LN", "DMjr", "Level"]

    if any(field not in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    ID_S = data["ID_S"]

    if not is_strict_int(ID_S) or ID_S <= 0:
        return jsonify({"error": "ID_S must be a positive integer"}), 400

    if find_student(ID_S) is not None:
        return jsonify({"error": "Student ID already exists"}), 409

    error = validate_student_fields(
        data["FN"], data["LN"], data["DMjr"], data["Level"]
    )
    if error:
        return error

    student = Student(
        ID_S, data["FN"].strip(), data["LN"].strip(),
        data["DMjr"], data["Level"]
    )
    students.append(student)

    return jsonify(student.to_dict()), 201


@app.route("/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    data, error = read_json()

    if error:
        return error

    FN = data.get("FN", student.FN)
    LN = data.get("LN", student.LN)
    DMjr = data.get("DMjr", student.DMjr)
    Level = data.get("Level", student.Level)

    error = validate_student_fields(FN, LN, DMjr, Level)
    if error:
        return error

    student.FN = FN.strip()
    student.LN = LN.strip()
    student.DMjr = DMjr
    student.Level = Level

    return jsonify(student.to_dict()), 200


@app.route("/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    students.remove(student)

    return jsonify({"message": "Student deleted"}), 200


# ==================================================
#                      REPORTS
#                (ALL ROUTES ARE PUBLIC)
# ==================================================

@app.route("/reports", methods=["GET"])
def get_all_reports():
    return jsonify([r.to_dict() for r in reports]), 200


@app.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = find_report(report_id)

    if report is None:
        return jsonify({"error": "Report not found"}), 404

    return jsonify(report.to_dict()), 200


@app.route("/reports", methods=["POST"])
def post_report():
    data, error = read_json()

    if error:
        return error

    required = ["ID_R", "Title", "Type", "K1", "K2", "K3", "Release_Date"]

    if any(field not in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    ID_R = data["ID_R"]

    if not is_strict_int(ID_R) or ID_R <= 0:
        return jsonify({"error": "ID_R must be a positive integer"}), 400

    if find_report(ID_R) is not None:
        return jsonify({"error": "Report ID already exists"}), 409

    error = validate_report_fields(
        data["Title"], data["Type"], data["K1"], data["K2"], data["K3"],
        data["Release_Date"]
    )
    if error:
        return error

    report = Report(
        ID_R,
        data["Title"].strip(),
        data["Type"].strip(),
        data["K1"].strip(),
        data["K2"].strip(),
        data["K3"].strip(),
        data["Release_Date"],
    )
    reports.append(report)

    return jsonify(report.to_dict()), 201


@app.route("/reports/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    report = find_report(report_id)

    if report is None:
        return jsonify({"error": "Report not found"}), 404

    data, error = read_json()

    if error:
        return error

    Title = data.get("Title", report.Title)
    Type = data.get("Type", report.Type)
    K1 = data.get("K1", report.K1)
    K2 = data.get("K2", report.K2)
    K3 = data.get("K3", report.K3)
    Release_Date = data.get("Release_Date", report.Release_Date)

    error = validate_report_fields(Title, Type, K1, K2, K3, Release_Date)
    if error:
        return error

    report.Title = Title.strip()
    report.Type = Type.strip()
    report.K1 = K1.strip()
    report.K2 = K2.strip()
    report.K3 = K3.strip()
    report.Release_Date = Release_Date

    return jsonify(report.to_dict()), 200


@app.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    report = find_report(report_id)

    if report is None:
        return jsonify({"error": "Report not found"}), 404

    reports.remove(report)

    return jsonify({"message": "Report deleted"}), 200


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)