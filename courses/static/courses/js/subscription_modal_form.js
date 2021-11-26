// document.getElementById('form_id').style.display = "none";

var formCheckLabel = document.getElementsByClassName('form-check-input');
var cardLevel = document.getElementsByClassName('level');

function clickHandler(){ // declare a function that updates the state
  // for (var i = 0; i < cardLevel.length; i++) {
  //     cardLevel.item(i).classList.remove("bg-success");
  // }

  for (var i = 0; i < formCheckLabel.length; i++) {
    if (formCheckLabel.item(i).value == this.dataset.level_id) {
      formCheckLabel.item(i).checked = true;
    }
  }
  // this.classList.add("bg-success");
}

for (var i = 0; i < cardLevel.length; i++) {
    cardLevel.item(i).addEventListener('click', clickHandler); // associate the function above with the click event
}