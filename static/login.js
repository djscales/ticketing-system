$(document).ready(function() {
  $('.ui.form').form();

  $("#loginUsername").focus();

  $("#formLogin").submit(function() {
    $(this).addClass("loading");
  });
});