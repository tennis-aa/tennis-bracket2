let form = document.getElementById("player-form");
let table = document.getElementById("player-table");
table = table.getElementsByTagName("tbody")[0];
let bracketSize_select = document.getElementById("bracket-size");

let tr = document.createElement("tr");
let player_number = tr.appendChild(document.createElement("td"));
let player = tr.appendChild(document.createElement("td")).appendChild(document.createElement("input"));
let elo = tr.appendChild(document.createElement("td")).appendChild(document.createElement("input"));
elo.type = "number";
elo.value = 1500;
elo.step = 0.1;


function update_bracketsize() {
  let n = parseInt(bracketSize_select.value);
  let current_players = table.getElementsByTagName("tr");
  if (current_players.length > n) {
    for (let i=current_players.length-1; i>=n; --i) {
      current_players[i].remove();
    }
  }
  else {
    for (let i=current_players.length; i<n; ++i) {
      player_number.textContent = i+1;
      player.value = "player" + (i+1);
      player.name = "player" + i;
      elo.name = "elo" + i;
      table.appendChild(tr.cloneNode(true));
    }
  }
}

update_bracketsize()
