$(function () {
  //  SECTION Hamburger Menu
  $("#menu-toggle").click(function (e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
  });
  //   !SECTION

  //   SECTION Combodate
  feather.replace();
  $("#date").combodate({
    minYear: 1950,
    maxYear: 2020,
    customClass: "form-control",
  });
  //  !SECTION

  //   SECTION Bootstrap Related

  // SECTION Tooltip
  $('[data-toggle="tooltip"]').tooltip();
  // !SECTION Tooltip

  // SECTION  File Uploader
  $(".custom-file-input").on("change", function () {
    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
  });
  //  !SECTION File Uploader

  //   SECTION Accordian
  $(".collapse").collapse();
  $(".minimize").collapse();
  //  !SECTION Accordian

  //   !SECTION Boostrap Related

  //   SECTION Search Function
  $("#searchBar").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $("#patientDetails tr").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });

  $("#searchPatientRecord").keyup(function () {
    search_text($(this).val());
  });

  function search_text(value) {
    $(".card").each(function () {
      var found = "false";
      $(this).each(function () {
        if ($(this).text().toLowerCase().indexOf(value.toLowerCase()) >= 0) {
          found = "true";
        }
      });
      if (found == "true") {
        $(this).show();
      } else {
        $(this).hide();
      }
    });
  }
  //  !SECTION

  //   SECTION Table Sorter
  $("#patientTable").tablesorter({
    widthFixed: true,
  });
  //   !SECTION
});
