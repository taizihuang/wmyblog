var windowObject = {'closed': true};

function click1(link) {
    modal.style.display = "block";
    modalImg.src = link;
}

function click2() {
    modal.style.display = "none";
}

function copyText(text) {

}

function delayClick(text) {
    navigator.clipboard.writeText(text);
    setTimeout(() => {
        if (windowObject.closed) {
            windowObject = window.open('https://docs.qq.com/sheet/DR09JSkJqU3h0dGJn?tab=BB08J2', 'wmyblog_tag');
        }
    }, 100);

}