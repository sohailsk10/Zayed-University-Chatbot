$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-acronyms .modal-content").html("");
        $("#modal-acronyms").modal("show");
      },
      success: function (data) {
        $("#modal-acronyms .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#acronyms-table tbody").html(data.html_acronyms_list);
          $("#modal-acronyms").modal("hide");
        }
        else {
          $("#modal-acronyms .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // Create acronyms
  $(".js-create-acronyms").click(loadForm);
  $("#modal-acronyms").on("submit", ".js-acronyms-create-form", saveForm);

  // Update acronyms
  $("#acronyms-table").on("click", ".js-update-acronyms", loadForm);
  $("#modal-acronyms").on("submit", ".js-acronyms-update-form", saveForm);

  // Delete acronyms
  $("#acronyms-table").on("click", ".js-delete-acronyms", loadForm);
  $("#modal-acronyms").on("submit", ".js-acronyms-delete-form", saveForm);

});
