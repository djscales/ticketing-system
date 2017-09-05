import flask_sqlalchemy
import flask_login

db = flask_sqlalchemy.SQLAlchemy()

class Users(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False, server_default = "")

    email = db.Column(db.String(255), unique = True, nullable = True)   

    firstName = db.Column(db.String(100), nullable = True)
    lastName = db.Column(db.String(100), nullable = True)

    lastLogin = db.Column(db.DateTime, nullable = True)
    dateCreated = db.Column(db.DateTime, nullable = True)

    status = db.Column(db.String(1), nullable = True)
    statusNotes = db.Column(db.Text, nullable = True)
    statusDate = db.Column(db.DateTime, nullable = True)

class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    
    dateCreated = db.Column(db.DateTime, nullable = False)
    lastActivity = db.Column(db.DateTime, nullable = False)

    assigneeID = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = True)
    assignee = db.relationship("Users", foreign_keys = [assigneeID])

    creatorID = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    creator = db.relationship("Users", foreign_keys = [creatorID])

    title = db.Column(db.String(255), nullable = False)
    text = db.Column(db.Text, nullable = False)

    priority = db.Column(db.String(1), nullable = True)
    status = db.Column(db.String(1), nullable = True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    dateCreated = db.Column(db.DateTime, nullable = True)

    ticketID = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable = False)
    ticket = db.relationship("Tickets", foreign_keys = [ticketID])

    creatorID = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    creator = db.relationship("Users", foreign_keys = [creatorID])

    text = db.Column(db.Text, nullable = False)
    internalFlag = db.Column(db.Boolean(), nullable = False, server_default = "0")

class Files(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    commentID = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable = False)
    comment = db.relationship("Comments", foreign_keys = [commentID])

    data = db.Column(db.LargeBinary, nullable = False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    creatorID = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    creator = db.relationship("Users", foreign_keys = [creatorID])

    text = db.Column(db.Text, nullable = False)
