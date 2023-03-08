$(function () {

  /* Functions */
  
  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-rectification .modal-content").html("");
        $("#modal-rectification").modal("show");
      },
      success: function (data) {
        $("#modal-rectification .modal-content").html(data.html_form);
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
          $("#rectification-table tbody").html(data.html_rectification_list);
          $("#modal-rectification").modal("hide");
        }
        else {
          $("#modal-rectification .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // Create acronyms
  // $(".js-create-acronyms").click(loadForm);
  // $("#modal-acronyms").on("submit", ".js-acronyms-create-form", saveForm);

  // Update rectification
  $("#rectification-table").on("click", ".js-update-acronyms", loadForm);
  $("#modal-rectification").on("submit", ".js-acronyms-update-form", saveForm);

  // Delete rectification
  $("#rectification-table").on("click", ".js-delete-acronyms", loadForm);
  $("#modal-rectification").on("submit", ".js-acronyms-delete-form", saveForm);

});
