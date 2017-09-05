function HandleConnectionError() {
  $("#connectionErrorModal").modal("show");
}

function GetComments() {
  $.getJSON("getcomments", { "id": ticketID }, function(responseData) {
    directives = {
      "comment-internal-flag": {
        html: function() {
          if (this["comment-internal-flag"] === false) {
            return " - Comment";
          } else if (this["comment-internal-flag"] === true) {
            return "- Note";
          }
        }
      }
    };

    $("#ticket-comments").render(responseData, directives);
  });
}

function GetUsers() {
  $.getJSON("getusers", function(responseData) {
    $("#possible-users").render(responseData);
  });
}

function GetTicket() {
  $.getJSON("getticket", { "id": ticketID }, function(responseData) {
    directives = {
      "ticket-priority": {
        html: function() {
          if (this["ticket-priority"] === "L") {
            return "Low";
          } else if (this["ticket-priority"] === "M") {
            return "Medium";
          } else if (this["ticket-priority"] === "H") {
            return "High";
          }
        }
      }
    };

    $("#ticketInformation").render(responseData, directives);
  });
}

// -----

function form_new_ticket_Before() {
  $("#form-new-ticket").addClass("loading");
  $("#form-new-ticket-buttons .button").addClass("disabled");
}

function form_new_ticket_Success(responseData) {
  // Parse the incoming JSON from the server.
  var parsedData = JSON.parse(responseData);

  // If the request was successfully processed by the server...
  if (parsedData.status === "success") {
    $("#modal-new-ticket").modal("hide");
    $("#form-new-ticket").form("reset");
    $("#form-new-ticket").removeClass("error");

    // Reload the ticket list table.
    tlTable.ajax.reload();
  }

  // If it failed though, add the error class to the form.
  else if (parsedData.status === "failure") {
    $("#form-new-ticket").addClass("error");
    $("#form-new-ticket .error.message").transition("shake");
  }
}

function form_new_ticket_Error() {
  HandleConnectionError();
}

function form_new_ticket_Complete() {
  $("#form-new-ticket").removeClass("loading");
  $("#form-new-ticket-buttons .button").removeClass("disabled");
}

// -----

// Before sending the feedback modal AJAX request...
function form_feedback_Before() {
  $("#form-feedback").addClass("loading");
  $("#form-feedback-buttons .button").addClass("disabled");
  $("#form-feedback").removeClass("error");
}

// If the feedback modal AJAX request was successful...
function form_feedback_Success(responseData) {
  // Parse the incoming JSON from the server.
  var parsedData = JSON.parse(responseData);

  // If the request was successfully processed by the server...
  if (parsedData.status === "success") {
    $("#modal-feedback").modal("hide");
    $("#form-feedback").form("reset");
    $("#form-feedback").removeClass("error");
  }

  // If it failed though, add the error class to the form.
  else if (parsedData.status === "failure") {
    $("#form-feedback").addClass("error");
    $("#form-feedback .error.message").transition("shake");
  }
}

// If the feedback modal AJAX request experienced an error...
function form_feedback_Error() {
  HandleConnectionError();
}

// If the feedback modal AJAX request has completed...
function form_feedback_Complete() {
  $("#form-feedback").removeClass("loading");
  $("#form-feedback-buttons .button").removeClass("disabled");
}

// -----

function form_settings_Before() {
  $("#form-settings").addClass("loading");
  $("#form-settings-buttons .button").addClass("disabled");
}

function form_settings_Success() {
  $("#modal-settings").modal("hide");
  $("#form-settings").form("reset");
}

function form_settings_Error() {
  HandleConnectionError();
}

function form_settings_Complete() {
  $("#form-settings").removeClass("loading");
  $("#form-settings-buttons .button").removeClass("disabled");
}

// -----

function form_ticket_comment_Before() {
  $("#form-ticket-comment").addClass("loading");
}

function form_ticket_comment_Success(responseData) {
  // Parse the incoming JSON from the server.
  var parsedData = JSON.parse(responseData);

  // If the request was successfully processed by the server...
  if (parsedData.status === "success") {
    // Grab the ID of the ticket we just submitted a comment for. We will use this to fetch the proper (new)
    // list of comments.
    ticketID = $("#ftc-ticket-id").attr("value");

    $("#ftc-comment").val("");
    $("#ftc-private-comment").removeClass("active");
    $("#ftc-public-comment").addClass("active");
    $('#ftc-internal-flag').val("0");
    $("#ftc-comment").attr("placeholder", "Type a response to all users...");
    $("#form-ticket-comment").removeClass("error");
    $("#form-ticket-comment").removeClass("loading");

    // Make another JSON request to fetch the comment data and then render it into the GUI.
    GetComments();

    // Scroll to the new comment just made.
    $("html, body").animate({ scrollTop: $("#ticket-comments").first().offset().top }, 0);
  }

  // If it failed though, add the error class to the form.
  else if (parsedData.status === "failure") {
    $("#form-ticket-comment").addClass("error");
    $("#form-ticket-comment .error.message").transition("shake");

    // Scroll to the bottom so the error can be focused upon.
    $("html, body").animate({ scrollTop: $(document).height() }, 0);
  }
}

function form_ticket_comment_Error() {
  HandleConnectionError();
}

function form_ticket_comment_Complete() {
  $("#form-ticket-comment").removeClass("loading");
}