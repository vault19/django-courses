var reviewModal = document.getElementById('reviewModal');
var formErrors = document.getElementById('formErrors');


console.log(formErrors, typeof(formErrors));

if(typeof(formErrors) != 'undefined' && formErrors != null) {
  var reviewModalJSObject = new bootstrap.Modal(reviewModal);
  reviewModalJSObject.show();
}

reviewModal.addEventListener('show.bs.modal', function (event) {
  // Button that triggered the modal
  var button = event.relatedTarget;

  // Extract info from data-bs-* attributes
  var submission_id = button.getAttribute('data-bs-submission_id');
  var author_id = button.getAttribute('data-bs-author_id');

  // Update the modal's content.
  var SubmissionInput = document.getElementById("id_submission");
  SubmissionInput.value = submission_id;
  // SubmissionInput.setAttribute("disabled", "disabled");
  var AuthorInput = document.getElementById("id_author");
  AuthorInput.value = author_id;
  // AuthorInput.setAttribute("disabled", "disabled");
})