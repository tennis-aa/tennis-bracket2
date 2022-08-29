// These variables are defined in the template
// let bracketSize;
// let rounds;
// let counter;
// let players;
// let elo;
// let bracket;
let option_blank = document.createElement("option");
function loadFillout() {

  // Put players in the bracket
  for (let i = 0; i < players.length; i++) {
    let id = "p" + i;
    document.getElementById(id).innerHTML = players[i];
  }

  // Put select elements to pick winners in the first round
  for (let i = 0; i < bracketSize/2; i++){
    let sel = document.getElementById("select"+ (counter[1] + i));
    let option1 = document.createElement("option");
    let option2 = document.createElement("option");
    option1.innerHTML = players[2*i];
    option2.innerHTML = players[2*i+1];
    sel.appendChild(option1);
    sel.appendChild(option2);
    // Add info to tooltips from elo ratings
    let tip = document.getElementById("tip"+(counter[1]+i));
    if (tip) {
      let tds = tip.querySelectorAll("td");
      let prob = 10**(elo[2*i]/400)/(10**(elo[2*i]/400) + 10**(elo[2*i+1]/400));
      tds[0].innerHTML = players[2*i];
      tds[1].innerHTML = Math.round(prob*100) + "%";
      tds[2].innerHTML = players[2*i+1];
      tds[3].innerHTML = Math.round((1-prob)*100) + "%";
    }
  }
  // Put select elements to pick winners in other rounds
  for (let j=2; j<=rounds; j++) {
    for (let i=0; i<bracketSize/(2**j); i++) {
      let sel = document.getElementById("select"+ (counter[j] + i));
      sel.appendChild(option_blank.cloneNode(true));
      sel.appendChild(option_blank.cloneNode(true));
    }
  }
  // auto select byes
  for (let i = 0; i < bracketSize/2; i++){ 
    let sel = document.getElementById("select"+ (counter[1] + i));
    if (players[2*i]=="Bye") {
      sel.innerHTML = "";
      let opt = document.createElement("option");
      opt.innerHTML = players[2*i+1];
      sel.appendChild(opt);
      update_options(counter[1] + i);
      continue;
    } else if (players[2*i+1]=="Bye") {
      sel.innerHTML = "";
      let opt = document.createElement("option");
      opt.innerHTML = players[2*i];
      sel.appendChild(opt);
      update_options(counter[1] + i);
      continue;
    }
  }

  // select the players that are in database in first round
  for (let i = 0; i < bracketSize/2; i++){
    let sel = document.getElementById("select"+ (counter[1] + i));
    if (bracket[counter[1]+i-bracketSize] == players[2*i]) {
      sel.value = players[2*i];
      update_options(counter[1]+i);
    } else if (bracket[counter[1]+i-bracketSize] == players[2*i+1]) {
      sel.value = players[2*i+1];
      update_options(counter[1]+i);
    }
  }
  // select the players that are in database in other rounds
  for (let j=2; j<=rounds; j++) {
    for (let i=0; i<bracketSize/(2**j); i++) {
      let sel = document.getElementById("select"+ (counter[j] + i));
      if (bracket[counter[j]+i-bracketSize] == sel.options[1].value) {
        sel.value = sel.options[1].value;
        if (j<rounds) update_options(counter[j]+i);
      } else if (bracket[counter[j]+i-bracketSize] == sel.options[2].value) {
        sel.value = sel.options[2].value;
        if (j<rounds) update_options(counter[j]+i);
      }
    }
  }
}


// The following function should update the available options depending on the choices of the user
function update_options(player){
  let round;
  let place;
  for (let j=1; j<rounds; j++) {
    if (player >= counter[j]) {
      round = j;
      break;
    }
  }
  let i = player - counter[round];
  if (i % 2) { // odd
    playerNew = counter[round+1] + (i-1)/2;
    place = 2;
  } else { // even
    playerNew = counter[round+1] + i/2;
    place = 1;
  }
  let sel = document.getElementById("select"+player);
  let selNew = document.getElementById("select"+playerNew);
  selNew.options[place].innerHTML = sel.value;

  // Add info to tooltips from elo ratings
  let tip = document.getElementById("tip"+playerNew);
    if (tip) {
    let p1 = selNew.options[1].value;
    let p2 = selNew.options[2].value;
    let elo1 = elo[players.findIndex(element => element == p1)];
    let elo2 = elo[players.findIndex(element => element == p2)];
    let prob = 10**(elo1/400)/(10**(elo1/400) + 10**(elo2/400));
    let tds = tip.querySelectorAll("td");
    tds[0].innerHTML = p1;
    tds[2].innerHTML = p2;
    if (isNaN(prob)) {
      tds[1].innerHTML = "";
      tds[3].innerHTML = "";
    } else {
    tds[1].innerHTML = Math.round(prob*100) + "%";
    tds[3].innerHTML = Math.round((1-prob)*100) + "%";
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