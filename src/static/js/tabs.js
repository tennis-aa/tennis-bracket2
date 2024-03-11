let tabs = document.getElementById("tournament-navbar").children;
let tab_contents = [
  document.getElementById("display-bracket"),
  document.getElementById("table-container"),
  document.getElementById("fillout-bracket")
]

function open_tab(n) {
  for (let i=0; i<tabs.length; ++i) {
    if (i === n) {
      tabs[i].classList.add("active");
      tab_contents[i].classList.add("active");
    }
    else {
      tabs[i].classList.remove("active");
      tab_contents[i].classList.remove("active");

    }
  }
}

let user_select = document.getElementById("user");
function show_player_bracket(name) {
  // https://stackoverflow.com/a/31982533/12510953 exclude selection
  let selection = window.getSelection();
  if(selection.type != "Range") { 
    open_tab(0);
    user_select.value = name;
    display_bracket();
  }
}