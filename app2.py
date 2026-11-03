# app.py
import uuid
from flask import Flask, request
from flask_smorest import abort

from db import db

app = Flask(__name__)

# ---- startup ----
db.connect()
db.create_tables()


# ==================================================================
# REPORT
# ==================================================================

@app.get("/report/<string:report_id>")
def get_report(report_id):
    db.cursor.execute("SELECT * FROM report WHERE id = ?", (report_id,))
    row = db.cursor.fetchone()
    if row is None:
        abort(404, message="Report not found")
    return dict(row)


@app.post("/report")
def create_report():
    report_data = request.get_json()

    if "title" not in report_data or "type" not in report_data:
        abort(400, message="Missing required fields: title and type")

    # duplicate check (same title + type + student_id)
    db.cursor.execute(
        "SELECT id FROM report WHERE title = ? AND type = ? AND student_id = ?",
        (report_data["title"], report_data["type"], report_data["student_id"])
    )
    if db.cursor.fetchone() is not None:
        abort(400, message="Report with the same title already exists")

    # relationship check
    db.cursor.execute("SELECT id FROM student WHERE id = ?", (report_data["student_id"],))
    if db.cursor.fetchone() is None:
        abort(404, message="Student not found")

    report_id = uuid.uuid4().hex
    db.cursor.execute(
        "INSERT INTO report (id, student_id, title, type) VALUES (?, ?, ?, ?)",
        (report_id, report_data["student_id"], report_data["title"], report_data["type"])
    )
    db.commit()

    return {**report_data, "id": report_id}


@app.delete("/report/<string:report_id>")
def delete_report(report_id):
    db.cursor.execute("DELETE FROM report WHERE id = ?", (report_id,))
    db.commit()
    if db.cursor.rowcount == 0:
        abort(404, message="Report not found")
    return {"message": "Report deleted successfully"}


@app.put("/report/<string:report_id>")
def update_report(report_id):
    report_data = request.get_json()
    if "title" not in report_data or "type" not in report_data:
        abort(400, message="Missing required fields: title and type in the JSON payload")

    db.cursor.execute("SELECT id FROM report WHERE id = ?", (report_id,))
    if db.cursor.fetchone() is None:
        abort(404, message="Report not found")

    db.cursor.execute(
        "UPDATE report SET title = ?, type = ?, student_id = ? WHERE id = ?",
        (
            report_data["title"],
            report_data["type"],
            report_data.get("student_id", None) or _get_report_student(report_id),
            report_id,
        )
    )
    db.commit()

    db.cursor.execute("SELECT * FROM report WHERE id = ?", (report_id,))
    return dict(db.cursor.fetchone())


def _get_report_student(report_id):
    """Helper — returns current student_id of an existing report."""
    db.cursor.execute("SELECT student_id FROM report WHERE id = ?", (report_id,))
    return db.cursor.fetchone()["student_id"]


@app.get("/report")
def get_all_reports():
    db.cursor.execute("SELECT * FROM report")
    return {"reports": [dict(r) for r in db.cursor.fetchall()]}


# ==================================================================
# STUDENT
# ==================================================================

@app.get("/student/<string:student_id>")
def get_student(student_id):
    db.cursor.execute("SELECT * FROM student WHERE id = ?", (student_id,))
    row = db.cursor.fetchone()
    if row is None:
        abort(404, message="Student not found")
    student = dict(row)

    # show the relationship in the response
    db.cursor.execute("SELECT * FROM report WHERE student_id = ?", (student_id,))
    student["reports"] = [dict(r) for r in db.cursor.fetchall()]
    return student


@app.post("/student")
def add_student():
    student_data = request.get_json()

    if "fname" not in student_data or "lname" not in student_data:
        abort(400, message="Missing required fields: fname and lname")

    # duplicate check (same fname + lname)
    db.cursor.execute(
        "SELECT id FROM student WHERE fname = ? AND lname = ?",
        (student_data["fname"], student_data["lname"])
    )
    if db.cursor.fetchone() is not None:
        abort(400, message="Student with the same name already exists")

    student_id = uuid.uuid4().hex
    db.cursor.execute(
        "INSERT INTO student (id, fname, lname) VALUES (?, ?, ?)",
        (student_id, student_data["fname"], student_data["lname"])
    )
    db.commit()

    return {**student_data, "id": student_id}, 201


@app.get("/student")
def get_students():
    db.cursor.execute("SELECT * FROM student")
    return {"students": [dict(r) for r in db.cursor.fetchall()]}

@app.delete("/student/<string:student_id>")
def delete_student(student_id):
    db.cursor.execute("SELECT id FROM student WHERE id = ?", (student_id,))
    if db.cursor.fetchone() is None:
        abort(404, message="Student not found")

    # Because of ON DELETE CASCADE in db.py, deleting the student 
    # will automatically delete all their reports too!
    db.cursor.execute("DELETE FROM student WHERE id = ?", (student_id,))
    db.commit()
    return {"message": "Student deleted successfully"}

if __name__ == "__main__":
    app.run(debug=True)