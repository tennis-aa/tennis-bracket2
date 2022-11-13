// the following variables are loaded from the server through the template
// let players;
// let brackets;
// let bracketSize;
// let results_dict;
let results;
let scores;
let losers;
let table_results;
// Put players in the bracket
function loadDisplay() {
  for (let i = 0; i < players.length; i++) {
    let id = "p" + i;
    document.getElementById(id).textContent = players[i];
  }

  let sel = document.getElementById("user");
  let users = Object.keys(brackets);
  users.sort();
  for (let i=0; i<users.length; i++) {
    let opt = document.createElement("option");
    opt.textContent = users[i];
    sel.appendChild(opt)
  }

  results = results_dict["results"];
  scores = results_dict["scores"];
  losers = results_dict["losers"];
  table_results = results_dict["table_results"];
  for (let i = 0; i < results.length; i++) {
    if (results[i] != -1) {
      let id = "p" + (i+bracketSize);
      document.getElementById(id).textContent = players[results[i]];
    }
  }

  let params = new URLSearchParams(location.search);
  sel.value = params.get("user");
  sel.onchange();
}

function display_bracket() {
  let user = document.getElementById("user").value;
  let user_info_points = document.getElementById("user-info-points");
  let user_info_position = document.getElementById("user-info-position");
  if (user=="") {
    user_info_points.textContent = "";
    user_info_position.textContent = "";
    for (let i = 0; i < bracketSize-1; i++) {
      let player = document.getElementById("p" + (i+bracketSize));
      let score = document.getElementById("score"+ (i+bracketSize));
      if (results) {
        player.textContent = players[results[i]];
      } else {
        player.textContent = "";
      }
      player.style.color = "var(--myblack)";
      if (score && scores) {score.textContent = scores[i];}
    }
  } 
  else {
    let bracket = brackets[user];
    let user_loc = table_results.user.findIndex(element => element==user);
    if (user_loc != -1) {
      let nr_users = table_results.user.length;
      user_info_points.textContent = table_results.points[user_loc] + " puntos"; 
      user_info_position.textContent = "Posicion " + table_results.position[user_loc] + "/" + nr_users + " (" + table_results.rank[user_loc] + ")";
    }
    else {
      user_info_points.textContent = ""; 
      user_info_position.textContent = "";
    }
    for (let i = 0; i < bracket.length; i++) {
      let player = document.getElementById("p" + (i+bracketSize));
      let score = document.getElementById("score"+ (i+bracketSize));
      player.textContent = players[bracket[i]];
      if (score) score.textContent = "";
      if (!results) {
        player.style.color = "var(--myblack)";
        continue;
      }
      if (i<bracketSize/2 && (players[2*i]=="Bye" || players[2*i+1]=="Bye")) {
        player.style.color = "var(--myblack)";
      } else if (results[i]!=-1 && bracket[i]==results[i]) {
        player.style.color = "var(--color4)";
      } else if (losers.includes(bracket[i])){
        player.style.color = "var(--color5)";
      } else {
        player.style.color = "var(--myblack)";
      }
    }
  }
}
