import datetime
import json
import passlib.hash

import sqlalchemy

import flask
import flask_admin
import flask_admin.contrib.sqla
import flask_compress
import flask_mail
import flask_login

import models
import jsonops

DEBUG_FLAG = True

app = flask.Flask(__name__)
app.config.from_object(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "e135a5c2766b796fcbf286269fd59de11fa47e663230604252f68bbbe4dc132b"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 604800

with app.app_context():
    models.db.init_app(app)

    # Setup Flask-Compress.
    compress = flask_compress.Compress()
    compress.init_app(app)

    # Setup Flask-Admin and add our views.
    admin = flask_admin.Admin(app, name="Ticket Administration", template_mode="bootstrap3")
    admin.add_view(flask_admin.contrib.sqla.ModelView(models.Users, models.db.session))
    admin.add_view(flask_admin.contrib.sqla.ModelView(models.Tickets, models.db.session))
    admin.add_view(flask_admin.contrib.sqla.ModelView(models.Comments, models.db.session))
    admin.add_view(flask_admin.contrib.sqla.ModelView(models.Files, models.db.session))
    admin.add_view(flask_admin.contrib.sqla.ModelView(models.Feedback, models.db.session))

    # Setup Flask-Login.
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.session_protection = "strong"

    # Setup Flask-Mail
    mail = flask_mail.Mail()
    mail.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return models.db.session.query(models.Users).filter(models.Users.id == user_id).first()

@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")

@app.route("/tickets", methods=["GET"])
@flask_login.login_required
def tickets():
    if DEBUG_FLAG:
        print("Tickets route visited.")

    fullName = "%s %s" % (flask_login.current_user.firstName, flask_login.current_user.lastName)

    return flask.render_template("tickets.html", fullName=fullName)

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")

    elif flask.request.method == "POST":
        inputUsername = flask.request.form["username"]
        inputPassword = flask.request.form["password"]

        dbResult = (
            models.db.session.query(
                models.Users
            )
            .filter(models.Users.username == inputUsername)
        )

        if dbResult.count() == 0:
            return flask.redirect(flask.url_for("login"))

        userData = dbResult.first()

        passwordMatch = passlib.hash.scrypt.verify(inputPassword, userData.password)

        if passwordMatch:
            flask_login.login_user(userData)
            return flask.redirect(flask.url_for("tickets"))

        return flask.redirect(flask.url_for("login"))

@app.route("/logout", methods=["POST"])
@flask_login.login_required
def logout():
    if DEBUG_FLAG:
        print("Logout route visited.")

    flask_login.logout_user()

    return flask.redirect(flask.url_for("index"))

@app.route("/getcomments", methods=["GET"])
@flask_login.login_required
def getcomments():
    if DEBUG_FLAG:
        print("Getcomments route visited.")

    reqID = flask.request.args["id"]

    dbComments = (
        models.db.session.query(
            models.Comments
        )
        .filter(models.Comments.ticketID == reqID)
        .order_by(sqlalchemy.desc(models.Comments.dateCreated))
    )

    jsonComments = jsonops.MakeJSONCommentL(dbComments)

    return jsonComments

@app.route("/getticket", methods=["GET"])
@flask_login.login_required
def getticket():
    if DEBUG_FLAG:
        print("Getticket route visited.")

    reqID = flask.request.args["id"]

    dbTicket = models.db.session.query(models.Tickets).filter(models.Tickets.id == reqID).first()

    ticketID = dbTicket.id
    ticketTitle = dbTicket.title
    ticketText = dbTicket.text
    ticketDate = dbTicket.dateCreated.strftime("%m-%d-%Y at %I:%M %p")
    ticketCreator = "%s %s" % (dbTicket.creator.firstName, dbTicket.creator.lastName)
    ticketPriority = dbTicket.priority
    if dbTicket.assignee:
        ticketAssignee = "%s %s" % (dbTicket.assignee.firstName, dbTicket.assignee.lastName)
    else:
        ticketAssignee = "Unassigned"
    ticketLastActivity = dbTicket.lastActivity.strftime("%m-%d-%Y at %I:%M %p")

    return json.dumps({
        "ticket-id": ticketID,
        "ticket-title": ticketTitle,
        "ticket-text": ticketText,
        "ticket-date": ticketDate,
        "ticket-creator": ticketCreator,
        "ticket-priority": ticketPriority,
        "ticket-assignee": ticketAssignee,
        "ticket-activity": ticketLastActivity
    })

@app.route("/assigntoticket", methods=["POST"])
@flask_login.login_required
def assigntoticket():
    if DEBUG_FLAG:
        print("Assigntoticket route visited.")

    ticketID = flask.request.form["ticket-id"]

    currentDT = datetime.datetime.now()

    # Update the proper ticket.
    (
        models.db.session.query(
            models.Tickets
        )
        .filter(models.Tickets.id == ticketID)
        .update({
            "assigneeID": flask_login.current_user.id,
            "lastActivity": currentDT
        })
    )

    # Add a comment to the database stating that we've assigned to the ticket.
    comment = models.Comments(
        dateCreated=currentDT,
        creatorID=flask_login.current_user.id,
        ticketID=ticketID,
        text="Assigned to ticket.",
        internalFlag=False)

    models.db.session.add(comment)
    models.db.session.commit()

    return json.dumps({"status": "success"})

@app.route("/givefeedback", methods=["POST"])
@flask_login.login_required
def givefeedback():
    if DEBUG_FLAG:
        print("Feedback route visited.")

    # Pull the text out of the feedback form POST data.
    feedbackText = flask.request.form["form-feedback-text"]

    # Check to see how long it is excluding spaces, tabs, and newlines.
    if len("".join(feedbackText.split())) < 30:
        return json.dumps({"status": "failure"})

    newFeedback = models.Feedback(text=feedbackText, creatorID=flask_login.current_user.id)

    models.db.session.add(newFeedback)
    models.db.session.commit()

    # Once it is safely stored in the DB, then go ahead and send off an email.

    return json.dumps({"status": "success"})

@app.route("/settings", methods=["POST"])
@flask_login.login_required
def settings():
    if DEBUG_FLAG:
        print("Settings route visited.")

    return ""

@app.route("/ticketlist", methods=["GET"])
@flask_login.login_required
def ticketlist():
    if DEBUG_FLAG:
        print("Ticketlist route visited.")

    numRecords = flask.request.args["length"]
    criteria = flask.request.args["criteria"]

    # If the criteria is "My Tickets"
    if criteria == "m":
        dbResult = (
            models.db.session.query(
                models.Tickets
            )
            .filter(models.Tickets.assigneeID == flask_login.current_user.id)
            .order_by(sqlalchemy.desc(models.Tickets.id))
            .limit(numRecords)
        )

    # If the criteria is "Unassigned Tickets"
    elif criteria == "u":
        dbResult = (
            models.db.session.query(
                models.Tickets
            )
            .filter(models.Tickets.assigneeID is None)
            .order_by(sqlalchemy.desc(models.Tickets.id))
            .limit(numRecords)
        )

    # If the criteria is "Open Tickets"
    elif criteria == "o":
        dbResult = (
            models.db.session.query(
                models.Tickets
            )
            .filter(models.Tickets.status == "O")
            .order_by(sqlalchemy.desc(models.Tickets.id))
            .limit(numRecords)
        )

    # If the criteria is "Closed Tickets"
    elif criteria == "c":
        dbResult = (
            models.db.session.query(
                models.Tickets
            )
            .filter(models.Tickets.status == "C")
            .order_by(sqlalchemy.desc(models.Tickets.id))
            .limit(numRecords)
        )

    # If the criteria is "Recently Updated"
    elif criteria == "r":
        dbResult = (
            models.db.session.query(
                models.Tickets
            )
            .order_by(sqlalchemy.desc(models.Tickets.lastActivity))
            .limit(numRecords)
        )

    # If the criteria is "All Tickets"
    elif criteria == "a":
        dbResult = (
            models.db.session.query(
                models.Tickets
            ).order_by(sqlalchemy.desc(models.Tickets.id))
            .limit(numRecords)
        )

    # If we have retrieved more than 0 records, convert our returned DB information into JSON.
    jsonData = jsonops.MakeJSONTicketL(dbResult)

    # Send it to the frontend.
    return jsonData

@app.route("/getusers", methods=["GET"])
@flask_login.login_required
def getusers():
    if DEBUG_FLAG:
        print("Getusers route visited.")

    # Select all users in the database. This will be fed to the template below.
    dbResult = (
        models.db.session.query(
            models.Users
        )
        .order_by(sqlalchemy.asc(models.Users.firstName))
        .all()
    )

    jsonData = jsonops.MakeJSONUserL(dbResult)

    return jsonData

@app.route("/newcomment", methods=["POST"])
@flask_login.login_required
def newcomment():
    if DEBUG_FLAG:
        print("Newcomment route visited.")

    text = flask.request.form["ftc-comment"]
    ticketID = flask.request.form["ftc-ticket-id"]
    internalFlag = flask.request.form["ftc-internal-flag"]

    # Check to see that if the ticket comment has more than just whitespace and newline characters.
    # If it is not long enough, return an error. Also return an error if the ticket ID is missing.
    if (len("".join(text.split())) < 1) or (ticketID == ""):
        return json.dumps({"status": "failure"})

    if internalFlag == "0":
        internalFlag = False
    elif internalFlag == "1":
        internalFlag = True

    currentDT = datetime.datetime.now()

    # Find and set the creator of the comment to be the same as the owner of the current session.
    creatorID = flask_login.current_user.id
    creator = models.db.session.query(models.Users).filter(models.Users.id == creatorID).first()

    # Find and set the ticket to be the same as the selected ticket.
    ticket = models.db.session.query(models.Tickets).filter(models.Tickets.id == ticketID).first()

    # Make the a comment record with the information given above.
    comment = models.Comments(
        dateCreated=currentDT,
        creator=creator,
        ticket=ticket,
        text=text,
        internalFlag=internalFlag)

    # We also need to update the Last Activity field for the specified ticket.
    (
        models.db.session.query(
            models.Tickets
        )
        .filter(models.Tickets.id == ticketID)
        .update({
            "lastActivity": currentDT
        })
    )

    models.db.session.add(comment)
    models.db.session.commit()

    return json.dumps({"status": "success"})

@app.route("/newticket", methods=["POST"])
@flask_login.login_required
def newticket():
    if DEBUG_FLAG:
        print("Newticket route visited.")

    # Store the fields submitted by the user. They are all automatically escaped by Flask.
    formSummary = flask.request.form["fnt-summary"]
    formText = flask.request.form["fnt-text"]
    formAssignee = flask.request.form["fnt-assignee"]
    formPriority = flask.request.form["fnt-priority"]

    if (formSummary == "") or (formText == ""):
        return json.dumps({"status": "failure"})

    # If the value from the form is "unassigned" instead of a user ID, set the assignee variable to
    # None. This sets the respective foreign key column in the DB as null.
    if formAssignee == "":
        assignee = None

    # If a valid user ID was submitted by the form, cast it into an integer, locate the proper
    # record, and set the assignee to it.
    else:
        assigneeID = int(formAssignee)
        assignee = (
            models.db.session.query(
                models.Users
            )
            .filter(models.Users.id == assigneeID)
            .first()
        )

    # Find and set the creator of the ticket to be the same as the owner of the current session.
    creatorID = flask_login.current_user.id
    creator = models.db.session.query(models.Users).filter(models.Users.id == creatorID).first()

    # Set the summary, description, and priority to what was given in the form. This is redundant
    # but helps to separate any future logic that may come along.
    summary = formSummary
    text = formText
    priority = formPriority

    # Retrieve the current datetime which will be used as a timestamp.
    currentDT = datetime.datetime.now()

    ticket = models.Tickets(
        dateCreated=currentDT,
        lastActivity=currentDT,
        assignee=assignee,
        creator=creator,
        title=summary,
        text=text,
        priority=priority,
        status="O")

    models.db.session.add(ticket)
    models.db.session.commit()

    return json.dumps({"status": "success"})

if __name__ == "__main__":
    app.run()
