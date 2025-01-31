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

function generatepass() {
    // Generate random password min 12 characters max 24 characters with at least one uppercase letter, one lowercase letter, one number and one special character
    var password = '';
    var uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    var lowercase = 'abcdefghijklmnopqrstuvwxyz';
    var numbers = '0123456789';
    var special = '!@#$%^&*()_+~`|}{[]\\:;?><,./-=';
    var all = uppercase + lowercase + numbers + special;
    var length = Math.floor(Math.random() * (24 - 8 + 1)) + 12;
    for (var i = 0; i < length; i++) {
        password += all.charAt(Math.floor(Math.random() * all.length));
    }
    return password;
}

// Toggle password visibility
function showpass() {
    var icon = document.getElementById('showpass');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
};