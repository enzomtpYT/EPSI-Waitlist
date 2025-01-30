import('https://cdn.jsdelivr.net/npm/marked/marked.min.js')
 
function mark(element, text) {
    let dirty = marked.parse(text);
    let clean = DOMPurify.sanitize(dirty, {FORBID_TAGS: ['style']});
    element.innerHTML = clean;
    element.classList.add('markdown');
    hljs.highlightAll();
}

function popup(category, message) {
    console.log(`Popup [${category}]: ${message}`);
    const popup = document.createElement('div');
    popup.classList.add('popup');
    if (category == 'danger') {
        popup.classList.add('ferror');
    } else if (category == 'success') {
        popup.classList.add('fsuccess');
    }
    const span = document.createElement('span');
    span.classList.add('popuptext');
    span.textContent = message;
    popup.appendChild(span);
    document.body.appendChild(popup);

    setTimeout(function() {
        popup.remove();
    }, 6000);
}