import('https://cdn.jsdelivr.net/npm/marked/marked.min.js')

const socket = io({ transports: ['websocket'], secure: location.port == 443 });

function mark(element, text) {
    let dirty = marked.parse(text);
    let clean = DOMPurify.sanitize(dirty, {FORBID_TAGS: ['style']});
    element.innerHTML = clean;
    element.classList.add('markdown');
    hljs.highlightAll();
}

function toggleElement(element) {
    if (getComputedStyle(element).display === 'none') {
        element.style.display = 'flex';
        setTimeout(() => {
            element.style.opacity = 1;
        }, 5);
    } else {
        element.style.opacity = 0;
        setTimeout(() => {
            element.style.display = 'none';
        }, 200);
    }
}

function formatDuration(duration) {
    if (duration == null) {
        return '0s';
    }
    const [hours, minutes, seconds] = duration.split(':').map(Number);
    let formattedDuration = '';
    if (hours > 0) {
        formattedDuration += `${hours}h`;
    }
    if (minutes > 0 || hours > 0) {
        formattedDuration += `${minutes}m`;
    }
    formattedDuration += `${seconds}s`;
    return formattedDuration;
}

function popup(category, message) {
    console.log(`Popup [${category}]: ${message}`);
    const popup = document.createElement('div');
    popup.classList.add('popup');
    if (category == 'danger') {
        popup.classList.add('ferror');
    } else if (category == 'success') {
        popup.classList.add('fsuccess');
    } else if (category == 'info') {
        popup.classList.add('finfo');
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

    return new Promise((resolve) => {

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

        resolve(password);

    });
}

// Toggle password visibility
function showpass() {
    var icon = document.getElementById('showpass');
    var passwordInput = document.getElementById('password');
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