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

function afterLoad() {
    /* Resizer */

    var resize = document.querySelector("#resizer");
    if (!resize) {
        return;
    }
    var left = document.querySelector(".sideItemList");
    var container = document.querySelector(".tabmanagment");
    var moveX = left.getBoundingClientRect().width + resize.getBoundingClientRect().width / 2;
    var drag = false;

    resize.addEventListener("mousedown", function (e) {
        drag = true;
    });

    container.addEventListener("mousemove", function (e) {
        moveX = e.x;
        if (drag) {
           left.style.width = moveX - resize.getBoundingClientRect().width / 2 - container.getBoundingClientRect().left + "px";
           e.preventDefault();
        }
    });

    document.addEventListener("mouseup", function (e) {
        drag = false;
    });

    /* End Resizer */
}

function SwitchTheme() {
    document.querySelector("body").classList.toggle("DT");
    document.querySelector("body").classList.toggle("WT");
    localStorage.setItem("theme", document.querySelector("body").classList.contains("DT") ? "DT" : "WT");
    document.querySelector('.background').src = document.querySelector("body").classList.contains("DT") ? "https://files.catbox.moe/foa83u.webp" : "";
    document.querySelector('.ThemeSwitcher').innerHTML = document.querySelector("body").classList.contains("DT") ? `<i class="fa-regular fa-sun-bright"></i>` : `<i class="fa-regular fa-moon-stars"></i>`;
}

function InitTheme() {
    if (localStorage.getItem("theme") == "DT") {
        document.querySelector("body").classList.add("DT");
    } else {
        document.querySelector("body").classList.add("WT");
    }
    document.querySelector('.background').src = document.querySelector("body").classList.contains("DT") ? "https://files.catbox.moe/foa83u.webp" : "";
    document.querySelector('.ThemeSwitcher').innerHTML = document.querySelector("body").classList.contains("DT") ? `<i class="fa-regular fa-sun-bright"></i>` : `<i class="fa-regular fa-moon-stars"></i>`;
}

updateLinks();
observeMarkdownLinks();
InitTheme();