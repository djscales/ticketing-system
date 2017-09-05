var tlTable;

$(function() {
  // Make it so Transparency only recognizes the data-bind attribute.
  Transparency.matcher = function(element, key) {
    return element.el.getAttribute("data-bind") == key;
  };

  $('.ui.form').form();
  $('.ui.checkbox').checkbox();
  $('.ui.dropdown').dropdown();

  tlTable = $('#ticketlist').DataTable({
    searchDelay: 1000,
    serverSide: true,
    processing: false,
    bInfo: false,
    select: true,
    rowId: "id",
    dom: "<t>",
    ajax: {
      "url": "/ticketlist",
      "type": "GET",
      "data": {
        "criteria": function() {
          return $("#ticket-list-view").val();
        }
      },
      "error": HandleConnectionError,
    },
    columns: [
      { data: "id" },
      { data: "title" },
      { data: "assignee" },
      { data: "priority" },
      { data: "date" }
    ],
    lengthMenu: [
      [10, 20, 30, 40, 50],
      [10, 20, 30, 40, 50]
    ],
    columnDefs: [{
        "targets": 2,
        "render": function(data, type, row, meta) {
          if (data === "Unassigned") {
            return "<a>Accept</a>";
          } else {
            return data;
          }
        }
      },
      {
        "targets": 3,
        "render": function(data, type, row, meta) {
          if (data === "L") {
            return "Low";
          } else if (data === "M") {
            return "Med";
          } else if (data === "H") {
            return "High";
          } else {
            return data;
          }
        }
      }
    ]
  });

  // Disable the select information below the ticket list table.
  tlTable.select.info(false);

  // When a currently selected cell is selected again prevent the default behavior (HTTP request).
  tlTable.on("user-select", function(e, dt, type, cell, originalEvent) {
    if ($(cell.node()).closest("tr").hasClass("selected")) {
      e.preventDefault();
    }
  })

  setInterval(function() {
    tlTable.ajax.reload(null, false);
  }, 30000);

  $('#menu-account').dropdown({
    action: 'hide'
  });

  $('#global-message .close').on('click', function() {
    $('#global-message').remove();
  });

  // Here we specify the properties of the New Ticket modal.
  $('#modal-new-ticket')
    .modal('setting', 'closable', false)
    .modal('attach events', '.newticket.button', 'show')
    .modal({
      onDeny: function() {
        $("#form-new-ticket").form("reset");
        $("#form-new-ticket").removeClass("error");
      }
    });

  // Here we specify the properties of the Settings modal.
  $('#modal-settings')
    .modal('setting', 'closable', false)
    .modal('attach events', '.settings.item', 'show')
    .modal({
      onDeny: function() {
        $("#form-settings").form("reset");
        $("#form-settings").removeClass("error");
      }
    });

  // Here we specify the properties of the Feedback modal.
  $('#modal-feedback')
    .modal('setting', 'closable', false)
    .modal('attach events', '.feedback.item', 'show')
    .modal({
      onDeny: function() {
        $("#form-feedback").removeClass("error");
        $("#form-feedback").form("reset");
      }
    });

  // Here we specify the properties of the Signout modal.
  $('#modal-signout')
    .modal('setting', 'closable', false)
    .modal('attach events', '.signout.item', 'show');

  // Here we specify the properties of the Connection Error modal.
  $('#connectionErrorModal')
    .modal('setting', 'closable', false);

  // When the user clicks "Yes" under the signout modal...
  $('#form-signout').submit(function() {
    $('#form-signout').addClass('loading');
    $('#form-signout-buttons .button').addClass('disabled');
  });


  $('#newticketAssignee').dropdown({});

  $('#newticketObservers').dropdown({});

  $('#newticketPriority').dropdown({
    forceSelection: true
  });


  $('#ticketdet_priority').dropdown();

  $('#tvDetails').hide();

  $('#tvActivityOpt').on('click', function() {
    $('#tvDetailsOpt').removeClass('active');
    $('#tvActivityOpt').addClass('active');
    $('#tvDetails').hide();
    $('#tvActivity').show();
  });

  $('#tvDetailsOpt').on('click', function() {
    $('#tvActivityOpt').removeClass('active');
    $('#tvDetailsOpt').addClass('active');
    $('#tvActivity').hide();
    $('#tvDetails').show();
  });

  $('#ftc-public-comment').on('click', function() {
    $('#ftc-private-comment').removeClass('active');
    $('#ftc-public-comment').addClass('active');
    $('#ftc-internal-flag').val('0');
    $('#ftc-comment').attr('placeholder', 'Type a response to all users...');
  });

  $('#ftc-private-comment').on('click', function() {
    $('#ftc-public-comment').removeClass('active');
    $('#ftc-private-comment').addClass('active');
    $('#ftc-internal-flag').val('1');
    $('#ftc-comment').attr('placeholder', 'Type a response to all users in your group(s)...');
  });


  // When the New Ticket form is submitted send it via AJAX.
  $("#form-new-ticket").ajaxForm({
    url: "newticket",
    type: "post",
    beforeSend: form_new_ticket_Before,
    success: form_new_ticket_Success,
    error: form_new_ticket_Error,
    complete: form_new_ticket_Complete,
  });

  // When the Feedback form is submitted send it via AJAX.
  $("#form-feedback").ajaxForm({
    url: "givefeedback",
    type: "post",
    beforeSend: form_feedback_Before,
    success: form_feedback_Success,
    error: form_feedback_Error,
    complete: form_feedback_Complete,
  });

  // When the Settings form is submitted send it via AJAX.
  $("#form-settings").ajaxForm({
    url: "settings",
    type: "post",
    beforeSend: form_settings_Before,
    success: form_settings_Success,
    error: form_settings_Error,
    complete: form_settings_Complete,
  });

  // When the Ticket Comment form is submitted send it via AJAX.
  $("#form-ticket-comment").ajaxForm({
    url: "newcomment",
    type: "post",
    beforeSend: form_ticket_comment_Before,
    success: form_ticket_comment_Success,
    error: form_ticket_comment_Error,
    complete: form_ticket_comment_Complete,
  });

  // When the ticket list option is modified, retrieve JSON from the server, and then render it.
  $("#ticket-list-view").change(function() {
    tlTable.ajax.reload();
  });

  // Make it so a mouse pointer appears over the body of the table.
  $("#ticketlist > tbody").css("cursor", "pointer");

  // Make it so the "Accept" link under the Assignee column becomes underlined when hovered over.
  $("#ticketlist").on("mouseenter", "a", function() {
    $(this).css("text-decoration", "underline")
  });

  $("#ticketlist").on("mouseleave", "a", function() {
    $(this).css("text-decoration", "none")
  });

  // When a row is clicked, place the ticket ID into the hidden input within the ticket comment section
  // and fetch the ticket's data.
  $("#ticketlist > tbody").on("click", "tr", function() {
    // If the clicked on row is not already active...
    if (!$(this).hasClass("selected")) {
      ticketID = $(this).attr("id");

      // Set the ticket ID field in the comments form to be the same as the one we clicked on.
      $("#ftc-ticket-id").attr("value", ticketID);

      // Remove the error class from the form ticket comment form if it is present.
      $("#form-ticket-comment").removeClass("error");

      // Make a JSON request to fetch the ticket data and then render it into the GUI.
      GetTicket();

      // Make another JSON request to fetch the comment data and then render it into the GUI.
      GetComments();

      // Make another JSON request to fetch the users data and then render it into the GUI.
      GetUsers();
    }
  });

  // Trigger event when a link is clicked within the table. The only links that should be in the
  // table are within the Assignee column!
  $("#ticketlist").on("click", "a", function() {
    ticketID = $(this).closest("tr").attr("id");

    // Send an AJAX request to the server and notify them of the new assignee on the ticket
    // which has been clicked on.
    $.ajax({
      url: "assigntoticket",
      method: "post",
      data: {
        "ticket-id": ticketID,
      },
      // If we cannot fulfill the request due to an HTTP issue (connection or not) back out
      // and push a full-screen modal.
      error: HandleConnectionError,
      // If we were able to successfully assign to the ticket, we immediately refresh the table.
      // This can seem inefficient but another approach will introduce too much complexity.
      success: function() {
        // Make another JSON request to fetch the comment data and then render it into the GUI.
        GetComments();
        tlTable.ajax.reload();
      }
    });

    // When the ticket list option is modified, retrieve JSON from the server, and then render it.
    $("#possible-users").change(function() {
      tlTable.ajax.reload();
    });
  });
});