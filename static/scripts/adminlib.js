function deleteType(type, id) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
        fetch('/api/delete/'+type, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id
            })
        }).then(data => {
            if (data.ok) {
                document.getElementById(`deleteElement-${id}-${type}`).remove();
                popup('success', 'Élément supprimé avec succès.');
            } else {
                popup('danger', 'Une erreur est survenue lors de la suppression du candidat.');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    afterLoad();
});

function afterLoad() {
    /* Resizer */

    var resize = document.querySelector("#resizer");
    var left = document.querySelector(".sideItemList");
    var container = document.querySelector(".tabmanagment");
    var moveX = left.getBoundingClientRect().width + resize.getBoundingClientRect().width / 2;
    var drag = false;

    resize.addEventListener("mousedown", function (e) {
       drag = true;
       moveX = e.x;
    });

    container.addEventListener("mousemove", function (e) {
       moveX = e.x;
       if (drag) {
          left.style.width =
             moveX - resize.getBoundingClientRect().width / 2 + "px";
          e.preventDefault();
       }
    });

    container.addEventListener("mouseup", function (e) {
       drag = false;
    });

    /* End Resizer */
}