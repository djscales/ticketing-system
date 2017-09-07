import json

def MakeJSONTicketL(dbData):
    """Create a JSON data structure for the ticket list so 
    DataTables can parse it."""

    # If there are no tickets in the returned database query then return empty JSON data.
    # CAN BE EASILY REMOVED.
    if dbData.count() == 0:
        return json.dumps({
            "data": [{
                "id": "",
                "title": "",
                "assignee": "",
                "priority": "",
                "date": ""
            }]
        })

    tableData = []
    for t in dbData:
        ticketID = t.id
        ticketTitle = t.title
        ticketPriority = t.priority
        ticketDate = t.dateCreated.strftime("%m-%d-%y")

        # If the assignee is present and not None, create a full name.
        if t.assignee:
            ticketAssignee = "%s %s" % (t.assignee.firstName, t.assignee.lastName)

        # Else if the assignee is not present (ie, None), set it to Unassigned.
        else:
            ticketAssignee = "Unassigned"

        # Append this information to the our parsed information list.
        tableData.append({
            "id": ticketID,
            "title": ticketTitle,
            "assignee": ticketAssignee,
            "priority": ticketPriority,
            "date": ticketDate
        })

    return json.dumps({"data": tableData})

def MakeJSONUserL(dbData):
    """Create a JSON data structure for all existing users so Semantic-UI
    dropdown can parse it."""

    userData = [{"user-full-name": "Unassigned", "user-id": ""}]

    for user in dbData:
        fullName = "%s %s" % (user.firstName, user.lastName)
        userData.append({"user-full-name": fullName, "user-id": user.id})

    return json.dumps(userData)

def MakeJSONCommentL(dbData):
    """Create a JSON data structure for all comments associated to a ticket
    so Semantic-UI dropdown can parse it."""

    # If there are no comments in the returned database query then return empty JSON data.
    if dbData.count() == 0:
        return json.dumps([{
            "comment-creator": "",
            "comment-internal-flag": "",
            "comment-date": "",
            "comment-text": ""
        }])

    commentData = []
    for x in dbData:
        fullName = "%s %s" % (x.creator.firstName, x.creator.lastName)
        commentData.append({
            "comment-creator": fullName,
            "comment-internal-flag": x.internalFlag,
            "comment-date": x.dateCreated.strftime("%m-%d-%Y at %I:%M %p"),
            "comment-text": x.text
        })

    return json.dumps(commentData)
