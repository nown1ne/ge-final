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
        } else {
          questionHtml += `<input type="text" name="${response.key}">`;
        }

        questionHtml += `</div>`;
        $("#questions-container").append(questionHtml);
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
