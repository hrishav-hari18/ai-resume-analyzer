from models.user import db


class ResumeAnalysis(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100)
    )

    role = db.Column(
        db.String(100)
    )

    score = db.Column(
        db.Float
    )

    feedback = db.Column(
        db.Text
    )

    filename = db.Column(
        db.String(300)
    )