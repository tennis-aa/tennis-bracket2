// These variables are defined in the template
// let bracketSize;
// let rounds;
// let counter;
// let players;
// let elo;
// let bracket;
function loadFillout() {

  // Put players in the bracket
  for (let i = 0; i < players.length; i++) {
    let id = "p" + i;
    document.getElementById(id).textContent = players[i];
  }

  // Put select elements to pick winners in the first round
  for (let i = 0; i < bracketSize/2; i++) {
    update_options(counter[1] + i);
  }
  // auto select byes
  for (let i = 0; i < bracketSize/2; i++){ 
    let sel = document.getElementById("select"+ (counter[1] + i));
    let autowinner;
    if (players[2*i]=="Bye") {
      autowinner = 2*i+1;
    }
    else if (players[2*i+1]=="Bye") {
      autowinner = 2*i;
    }
    if (autowinner) {
      sel.replaceChildren();
      let opt = document.createElement("option");
      opt.value = autowinner;
      opt.textContent = players[autowinner];
      sel.appendChild(opt);
      update_selection(counter[1] + i);
    }
  }

  // select the players that are in database
  for (let j=1; j<=rounds; j++) {
    for (let i=0; i<bracketSize/(2**j); i++) {
      let sel = document.getElementById("select"+ (counter[j] + i));
      if (sel.options.length == 1) continue; // A bye that was already selected
      if (bracket[counter[j]+i-bracketSize] == sel.options[1].value) {
        sel.value = sel.options[1].value;
        if (j<rounds) update_selection(counter[j]+i);
      } else if (bracket[counter[j]+i-bracketSize] == sel.options[2].value) {
        sel.value = sel.options[2].value;
        if (j<rounds) update_selection(counter[j]+i);
      }
    }
  }
}

function get_round(match) {
  let round = rounds;
  for (let j=0; j<rounds; j++) {
    if (match < counter[j+1]) {
      round = j; break; }
  }
  return round;
}

// The following function should update the available options depending on the choices of the user
function update_selection(match) {
  let round = get_round(match);
  let i = match - counter[round];
  match_next_round = counter[round+1] + Math.floor(i/2);
  update_options(match_next_round);
}

function update_options(match) {
  let sel = document.getElementById("select"+match);
  let option1 = sel.options[1]
  let option2 = sel.options[2]
  let currentSelection = sel.value;
  let round = get_round(match);
  let parent1 = counter[round-1] + (match-counter[round])*2;
  let parent2 = parent1 + 1;
  if (round > 1) {
    let selparent1 = document.getElementById("select"+parent1)
    let selparent2 = document.getElementById("select"+parent2)
    option1.value = selparent1.value;
    option1.textContent = players[selparent1.value] || "";
    option2.value = selparent2.value;
    option2.textContent = players[selparent2.value] || "";
    update_tooltip(match);
    if (currentSelection != sel.value) {
      sel.value = "";
      update_selection(match);
    }
  }
  else {
    option1.value = parent1;
    option1.textContent = players[parent1];
    option2.value = parent2;
    option2.textContent = players[parent2];
    update_tooltip(match);
  }
}

function update_tooltip(match) {
  // Add info to tooltips from elo ratings
  let tip = document.getElementById("tip"+match);
  let sel = document.getElementById("select"+match);
  if (tip) {
    let p1 = sel.options[1].value;
    let p2 = sel.options[2].value;
    let elo1 = elo[p1];
    let elo2 = elo[p2];
    let prob = 10**(elo1/400)/(10**(elo1/400) + 10**(elo2/400));
    let tipplayers = tip.querySelectorAll(".tipplayer");
    let tipprobs = tip.querySelectorAll(".tipprob");
    tipplayers[0].textContent = players[p1];
    tipplayers[1].textContent = players[p2];
    if (isNaN(prob)) {
      tipprobs[0].textContent = "";
      tipprobs[1].textContent = "";
    } else {
      tipprobs[0].textContent = Math.round(prob*100) + "%";
      tipprobs[1].textContent = Math.round((1-prob)*100) + "%";
    }
  }
}

// The following function allows the user to save the bracket in json format
function save_bracket(){
  let bracket = [];
  let username = document.getElementById("user-name").value;
  username = username.replace(/\s{2,}/g, ' '); // remove double spaces in username
  username = username.trim(); // remove leading and trailing spaces
  for (let j = 1; j <= rounds; j++){
    for (let i = 0; i < bracketSize/(2**j); i++) {
      let selectNode = document.getElementById("select"+ (counter[j]+i));
      bracket.push(selectNode.value);
    }
  }
  let entry = {};
  entry[username] = bracket;
  let blob = new Blob([JSON.stringify(entry)],{type : "application:json"});
  url = URL.createObjectURL(blob);
  let link = document.createElement('a');
  link.href = url;
  link.setAttribute("download",username + ".json");
  link.click();
}