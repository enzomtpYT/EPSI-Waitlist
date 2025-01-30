function updateLinks() {
    const markdownLinks = document.querySelectorAll('.markdown a');
    markdownLinks.forEach(link => {
        link.onclick = function(event) {
            if (!window.confirm('Vous allez être rediriger vers "' + link.href + '".\n\nVoulez-vous continuer ?')) {
                event.preventDefault();
            }
        };
    });
}

function observeMarkdownLinks() {
    const targetNodes = document.querySelectorAll('.markdown');
    const config = { childList: true, subtree: true };

    const callback = function(mutationsList, observer) {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                console.log('A child node has been added or removed.');
                updateLinks();
            }
        }
    };

    const observer = new MutationObserver(callback);
    targetNodes.forEach(node => observer.observe(node, config));
}

updateLinks();
observeMarkdownLinks();

