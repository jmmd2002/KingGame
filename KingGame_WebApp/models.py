from database import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    firsts = db.Column(db.Integer, default=0)
    seconds = db.Column(db.Integer, default=0)
    thirds = db.Column(db.Integer, default=0)
    fourths = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f"<Player {self.name}>"
