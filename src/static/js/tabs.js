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