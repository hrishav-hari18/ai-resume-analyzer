import os
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from models.user import db, User
from models.interview_model import Interview
from models.resume_model import ResumeAnalysis

from services.resume_analyzer import analyze_resume

from services.interview import (
    start_session,
    is_active,
    end_session,
    generate_question,
    evaluate_answer,
    extract_score
)

from services.file_parser import extract_resume_text
from services.resume_feedback import generate_resume_feedback


# ================= APP =================

app = Flask(__name__)


# ================= CORS FIX =================

CORS(
    app,
    resources={
        r"/*": {
            "origins": "*"
        }
    }
)


# ================= CONFIG =================

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///app.db"

app.config[
    "JWT_SECRET_KEY"
] = os.environ.get(
    "JWT_SECRET_KEY",
    "mysecret"
)


# ================= INIT =================

db.init_app(app)

bcrypt = Bcrypt(app)

jwt = JWTManager(app)

with app.app_context():
    db.create_all()


# ================= LOAD ROLES =================

with open("data/job_roles.json") as f:

    roles_data = json.load(f)


# ================= STORAGE =================

sessions = {}

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ================= HOME =================

@app.route("/")
def home():

    return "Backend running"


# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    existing_user = User.query.filter(
        (User.username == data["username"])
        |
        (User.email == data["email"])
    ).first()


    if existing_user:

        return jsonify({

            "error":
            "Username or Email already registered"

        }), 400


    if data["password"] != data[
        "confirm_password"
    ]:

        return jsonify({

            "error":
            "Passwords do not match"

        }), 400


    hashed = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")


    user = User(

        full_name=data["full_name"],

        username=data["username"],

        email=data["email"],

        password=hashed
    )


    db.session.add(user)

    db.session.commit()


    return jsonify({

        "message":
        "Registration successful"

    })


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    user = User.query.filter_by(
        username=data["username"]
    ).first()


    if not user:

        return jsonify({

            "error":
            "User not found"

        }), 400


    if not bcrypt.check_password_hash(
        user.password,
        data["password"]
    ):

        return jsonify({

            "error":
            "Wrong password"

        }), 400


    token = create_access_token(
        identity=user.username
    )


    return jsonify({

        "token": token,

        "username": user.username,

        "full_name": user.full_name

    })


# ================= PROFILE =================

@app.route("/profile")
@jwt_required()
def profile():

    username = get_jwt_identity()

    user = User.query.filter_by(
        username=username
    ).first()


    return jsonify({

        "full_name": user.full_name,

        "username": user.username,

        "email": user.email

    })


# ================= DASHBOARD =================

@app.route("/dashboard")
@jwt_required()
def dashboard():

    username = get_jwt_identity()


    resumes = ResumeAnalysis.query.filter_by(
        username=username
    ).all()


    interviews = Interview.query.filter_by(
        username=username
    ).all()


    resume_data = []

    for r in resumes:

        resume_data.append({

            "role": r.role,

            "score": r.score,

            "filename": r.filename,

            "feedback": r.feedback
        })


    interview_data = []

    for i in interviews:

        interview_data.append({

            "role": i.role,

            "score": i.score,

            "feedback": i.feedback
        })


    return jsonify({

        "resumes": resume_data,

        "interviews": interview_data

    })


# ================= ROLES =================

@app.route("/roles")
def roles():

    return jsonify(
        list(roles_data.keys())
    )


# ================= ANALYZE =================

@app.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():

    username = get_jwt_identity()

    role = request.form.get(
        "role",
        ""
    )


    if role not in roles_data:

        return jsonify({

            "error":
            "Invalid role"

        }), 400


    if "resume" not in request.files:

        return jsonify({

            "error":
            "Resume file missing"

        }), 400


    file = request.files["resume"]


    path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(path)


    resume_text = extract_resume_text(path)

    jd = roles_data[role]


    score = analyze_resume(
        resume_text,
        jd
    )


    feedback = generate_resume_feedback(
        resume_text,
        role,
        score
    )


    record = ResumeAnalysis(

        username=username,

        role=role,

        score=score,

        feedback=feedback,

        filename=file.filename
    )


    db.session.add(record)

    db.session.commit()


    return jsonify({

        "score": score,

        "feedback": feedback

    })


# ================= START INTERVIEW =================

@app.route("/start", methods=["POST"])
@jwt_required()
def start():

    username = get_jwt_identity()

    data = request.json or {}

    role = data.get(
        "role",
        ""
    )

    duration = data.get(
        "duration",
        10
    )


    session = start_session(
        duration
    )

    session["role"] = role

    sessions[username] = session


    q = generate_question(
        role,
        []
    )


    session["questions"].append(q)


    return jsonify({

        "question": q

    })


# ================= NEXT QUESTION =================

@app.route("/next", methods=["POST"])
@jwt_required()
def next_q():

    username = get_jwt_identity()

    data = request.json or {}

    answer = data.get(
        "answer",
        ""
    )


    if username not in sessions:

        return jsonify({

            "error":
            "Session not found"

        }), 400


    session = sessions[username]


    if not is_active(session):

        return jsonify({

            "end": True,

            "result":
            end_session(session)

        })


    last_q = session[
        "questions"
    ][-1]


    eval_text = evaluate_answer(

        last_q,

        answer,

        session["role"]
    )


    score = extract_score(
        eval_text
    )


    session["scores"].append(score)

    session["answers"].append(answer)


    session["history"].append(

        f"Q:{last_q} A:{answer}"
    )


    q = generate_question(

        session["role"],

        session["history"]
    )


    session["questions"].append(q)


    return jsonify({

        "question": q,

        "evaluation": eval_text,

        "score": score

    })


# ================= END INTERVIEW =================

@app.route("/end", methods=["POST"])
@jwt_required()
def end():

    username = get_jwt_identity()


    if username not in sessions:

        return jsonify({

            "error":
            "Session not found"

        }), 400


    result = end_session(
        sessions[username]
    )


    record = Interview(

        username=username,

        role=sessions[username]["role"],

        score=result["final_score"],

        feedback=str(result)
    )


    db.session.add(record)

    db.session.commit()


    return jsonify(result)


# ================= MAIN =================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port
    )