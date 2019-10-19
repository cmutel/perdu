// Populate last column of every row with a button

var table = document.getElementById("search_results_table");
// Iterate through rows
for (var i = 0, row; row = table.rows[i]; i++) {
    // Skip if parent of row is <thead>
    if (!(row.parentElement.tagName == "THEAD")){
        // Get first cell of the row
        var first_cell = row.cells[0];
        // Store its value
        var search_item = first_cell.innerHTML;
        // Get last cell of the row
        var last_cell = row.cells[row.cells.length-1];
        // Create button
        var btn = document.createElement('input');
        btn.type = "button";
        btn.value = "Find a match";
        btn.data = search_item
        btn.addEventListener('click', function() {
            show_modal(this);
        }, false);
        last_cell.appendChild(btn);
    };

}

function query(val_to_query){

    // Get the values of checked box
    var array = []
    var checkboxes = document.querySelectorAll('input[type=checkbox]:checked')

    var item_to_match = document.getElementById('label_item_to_match').innerHTML

    for (var i = 0; i < checkboxes.length; i++) {
      array.push(checkboxes[i].value)
    }

    if (array.length == 0) {
        alert("At least one catalogue needs to be selected.")
        return;
    };

    if (array.length>1){
        var catalogue = "all";
    } else {
        var catalogue = array[0];
    };

    var opts = {
      method: 'GET',
      headers: {}
    };
    fetch('/get_search_results/'+catalogue+'/'+val_to_query, opts).then(function (response) {
      return response.json();
    })
    .then(function (body) {
        // Select table in modal
        var table = document.getElementById("response_table")
        table.innerHTML = "";
        var th = document.createElement('tr');
        th.innerHTML = '<th>Name</th><th>Action</th>'
        table.appendChild(th);
        for (var row in body){
            if (body[row].length>0){
                var tr = document.createElement('tr');
                var btn = document.createElement('input');
                btn.className = "button-primary";
                btn.type = "submit";
                btn.value = "Select";
                btn.style = "float:right;margin:5px;";
                btn.setAttribute('data', body[row][0].toString().slice(0,40));
                btn.setAttribute('data-origin', item_to_match);
                btn.onclick = function() {exit_modal(this);};

                var div_label = document.createElement('div');
                div_label.className="tooltip";
                div_label.innerHTML = body[row][0].toString().slice(0,40);
                var tooltip = document.createElement('span')
                tooltip.className = "tooltiptext";
                tooltip.innerHTML = body[row][1].toString();
                div_label.append(tooltip);
                var td_label = document.createElement('td');
                var td_button = document.createElement('td');
                td_label.append(div_label);
                td_button.append(btn);
                tr.append(td_label);
                tr.append(td_button);
                table.append(tr);
            };
        };

    });
};

function show_modal(b){
    // Select modal
    var modal = document.getElementById('modal_match')
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      modal.style.display = "none";
    }
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }
    // Insert titles, etc.
    var title_span = document.getElementById("item_to_match")
    title_span.innerHTML = "<h2 id='label_item_to_match'>"+b.data+"</h2>";
    // Fetch data
    query(b.data);
    // Display modal
    modal.style.display = "block";
    };

function exit_modal(btn){
    var match = btn.getAttribute("data");
    var item_to_search_for = btn.getAttribute("data-origin");
    var table = document.getElementById("search_results_table");

    // Iterate through rows
    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.cells[0].innerHTML == item_to_search_for){
            row.cells[2].innerHTML = match;
            // Hide modal
            var modal = document.getElementById('modal_match')
            modal.style.display = "none";
            // Send selection to web app
            var payload = {
                'item to match': item_to_search_for,
                'match': match
            };

            var data = new FormData();
            data.append( "json", JSON.stringify(payload) );

            fetch("/file/<hash>/selection",
            {
                method: "POST",
                body: data
            });


            return;
        };
    };

};

// Populate table with search results as the search field is updated.
var table = document.getElementById('search_input');
table.addEventListener('input', function (evt) {
    query(this.value);
});

