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