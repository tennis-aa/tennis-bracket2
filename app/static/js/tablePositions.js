// The following variables are defined in the template
// let table_results;

function loadTable() {

  let nr_users = table_results.user.length;
  for (let i=0; i<nr_users; i++) {
    table_row = document.createElement("tr");
    // Add position
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.position[i]));
    table_row.appendChild(table_entry);

    // Add user name
    table_entry = document.createElement("td");
    link = document.createElement("a");
    link.href = "./?user=" + table_results.user[i];
    link.appendChild(document.createTextNode(table_results.user[i]));
    table_entry.appendChild(link);
    table_row.appendChild(table_entry);

    // Add points
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.points[i]));
    table_row.appendChild(table_entry);

    // Add potential points
    try {
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.potential[i]));
    table_row.appendChild(table_entry);
    } catch (error) {
      console.log(error);
    }
    // Add rank
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.rank[i]));
    table_row.appendChild(table_entry);

    // Add rank among monkeys
    try {
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.monkey_rank[i] + "% \u00B11%"));
    table_row.appendChild(table_entry);
    } catch (error) {
      console.log(error);
    }

    // Add rank among bots
    try {
    table_entry = document.createElement("td");
    table_entry.appendChild(document.createTextNode(table_results.bot_rank[i] + "% \u00B11%"));
    table_row.appendChild(table_entry);
    } catch (error) {
      console.log(error);
    }

    // Add probability of winning
    try {
      table_entry = document.createElement("td");
      table_entry.appendChild(document.createTextNode((table_results.prob_winning[i]*100).toFixed(1) + "% \u00B11%"));
      table_row.appendChild(table_entry);
      } catch (error) {
        console.log(error);
      }

    // Add row to table
    table = document.getElementById("table-positions");
    table.appendChild(table_row);
  }
}
