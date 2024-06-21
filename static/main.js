$(document).ready(function () {
  let answers = {};

  function loadNextQuestion() {
    $.ajax({
      url: "/next_question",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(answers),
      success: function (response) {
        if (response.key === null) {
          $("#submit-btn").show();
          return;
        }

        let questionHtml = `<div class="question" data-key="${response.key}">
                <p>${response.question}</p>`;

        if (response.options.length > 0) {
          response.options.forEach((option) => {
            questionHtml += `<label><input type="radio" name="${response.key}" value="${option}"> ${option}</label><br>`;
          });
        } else if (response.type === "file") {
          questionHtml += `<input type="file" id="${response.key}" name="${response.key}"><button id="upload-${response.key}">Upload</button>`;
        } else {
          let inputType = response.type === "number" ? "number" : "text";
          questionHtml += `<input type="${inputType}" name="${response.key}">`;
        }

        questionHtml += `</div>`;
        $("#questions-container").append(questionHtml);
        $(`#questions-container input[name="${response.key}"]`).focus(); // Focus on the new input field
      },
    });
  }

  $(document).on("change", ".question input", function () {
    let key = $(this).closest(".question").data("key");
    let value = $(this).val();
    answers[key] = value;

    $(this).closest(".question").nextAll().remove(); // Remove following questions
    loadNextQuestion(); // Load the next question
  });

  $(document).on("click", ".question button", function (e) {
    e.preventDefault();
    let key = $(this).attr("id").replace("upload-", "");
    let fileInput = $(`#${key}`)[0];

    if (fileInput.files.length > 0) {
      let file = fileInput.files[0];
      let formData = new FormData();
      formData.append(key, file);

      $.ajax({
        url: "/upload_file",
        method: "POST",
        processData: false,
        contentType: false,
        data: formData,
        success: function (response) {
          answers[key] = response.filePath;
          $(`.question[data-key="${key}"]`).nextAll().remove(); // Remove following questions
          loadNextQuestion(); // Load the next question
        },
      });
    } else {
      alert("Please select a file to upload.");
    }
  });

  $(document).on("keypress", ".question input", function (e) {
    if (e.which === 13) {
      // Enter key pressed
      e.preventDefault(); // Prevent form submission
      let key = $(this).closest(".question").data("key");
      let value = $(this).val();
      answers[key] = value;

      $(this).closest(".question").nextAll().remove(); // Remove following questions
      loadNextQuestion(); // Load the next question
    }
  });

  // Prevent form submission on Enter key press
  $("#questionnaire-form").submit(function (e) {
    e.preventDefault();
    // Handle form submission
    $.ajax({
      url: "/submit_answers",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(answers),
      success: function (response) {
        // Clear the form
        $("#questions-container").empty();
        $("#submit-btn").hide();
        $("#heading").hide();
        $("#questionnaire-form").hide();
        // Display the markdown response
        let markdownContainer = $('<div id="markdown-response"></div>');
        markdownContainer.html(marked.parse(response.markdown));
        $("#questionnaire-form").after(markdownContainer);
      },
      error: function (xhr, status, error) {
        console.error("Error submitting form:", error);
        alert("An error occurred while submitting the form. Please try again.");
      },
    });
  });

  loadNextQuestion(); // Initial load
});
