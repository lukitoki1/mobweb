window.addEventListener("load", popupsHandler);

function popupsHandler() {
    var source = new EventSource('/publications/stream');
    var out = document.getElementById('out');
    source.onmessage = function (e) {
        console.log(e.data);
        out.setAttribute("class", "visible");
        out.innerHTML = "Dodano nową publikację o tytule " + e.data + "\n" + "Odśwież by ją zobaczyć!\n" + out.innerHTML;
    };
}