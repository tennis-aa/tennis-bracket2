// the following variables are loaded from the server through the template
// let players;
// let brackets;
// let bracketSize;
// let results_dict;
let results;
let scores;
let losers;
let table_results
// Put players in the bracket
function loadDisplay() {
  for (let i = 0; i < players.length; i++) {
    let id = "p" + i;
    document.getElementById(id).innerHTML = players[i];
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
    let id = "p" + (i+bracketSize);
    document.getElementById(id).innerHTML = results[i];
  }

  let params = new URLSearchParams(location.search);
  sel.value = params.get("user");
  sel.onchange();
}

function display_bracket() {
  let user = document.getElementById("user").value;
  let user_info = document.getElementById("user-info");
  if (user==""){
    user_info.innerHTML = "";
    for (let i = 0; i < bracketSize-1; i++) {
      let player = document.getElementById("p" + (i+bracketSize));
      let score = document.getElementById("score"+ (i+bracketSize));
      if (results) {
        player.innerHTML = results[i];
      } else {
        player.innerHTML = "";
      }
      player.style.color = "black";
      if (score && scores) {score.textContent = scores[i];}
    }
  } else {
    let bracket = brackets[user];
    if (table_results) {
    let user_loc = table_results.user.findIndex(element=> element==user);
    let nr_users = table_results.user.length;
    user_info.innerHTML =  table_results.points[user_loc] + " puntos" + "<br>" + "Posicion " + table_results.position[user_loc] + "/" + nr_users + " (" + table_results.rank[user_loc] + ")";
    }
    for (let i = 0; i < bracket.length; i++) {
      let player = document.getElementById("p" + (i+bracketSize));
      let score = document.getElementById("score"+ (i+bracketSize));
      player.innerHTML = bracket[i];
      if (score) score.innerHTML = "";
      if (!results) {
        player.style.color = "black";
        continue;
      }
      if (i<bracketSize/2 && (players[2*i]=="Bye" || players[2*i+1]=="Bye")) {
        player.style.color = "black";
      } else if (results[i]!="" && bracket[i]==results[i]) {
        player.style.color = "green";
      } else if (losers.includes(bracket[i])){
        player.style.color = "red";
      } else {
        player.style.color = "black";
      }
    }
  }
}
