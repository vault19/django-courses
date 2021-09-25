var iframe = document.querySelector('iframe');
var player = new Vimeo.Player(iframe);
player.setColor('#1da1f2');

var prev_time = new Date().getTime();
var current_time = new Date().getTime();
const upload_time = 10000;

player.on('timeupdate', function(data) {
  player.getPlayed().then(function(played) {
      current_time = new Date().getTime();

      if((current_time - prev_time) > upload_time) {

          var xhr = new XMLHttpRequest();
          xhr.open("POST", window.location.pathname + "video-ping/", true);
          xhr.setRequestHeader("Content-Type", "application/json");
          xhr.setRequestHeader("X-CSRFToken", document.getElementById("ajax_csrf_token").elements["csrfmiddlewaretoken"].value);

          xhr.onreadystatechange = function() {
              if (this.readyState==4 && this.status==200) {
                  // Response
                  var response = this.responseText;
                  console.log(response);
              }
          };
          var data = {'watched_video_time_range': played};
          xhr.send(JSON.stringify(data));
          console.log(data);

          prev_time = new Date().getTime();
      }
  }).catch(function(error) {
      console.log('Error has occurred while updating video watched time...');
      console.log(error);
  });
});
