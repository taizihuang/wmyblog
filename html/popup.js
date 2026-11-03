const popup = document.getElementById('selection-popup');
var searchText = "";

function handleSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (!selectedText) {
        popup.style.display = 'none';
        return;
    } else {
        searchText = selectedText;
    }

    try {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // 过滤掉宽高为0的纯光标点击
        if (rect.width === 0 && rect.height === 0) {
            popup.style.display = 'none';
            return;
        }

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        // 1. 先临时显示获取弹窗的宽度
        popup.style.display = 'block';
        const popupWidth = popup.offsetWidth;
        const popupHeight = popup.offsetHeight;

        // 2. 计算理想的居中位置
        let left = rect.left + scrollLeft + (rect.width / 2) - (popupWidth / 2);
        let top = rect.top + scrollTop - popupHeight - 10; // 放在选区上方 10px

        // 3. 【关键】手机端屏幕边界防溢出处理
        const screenWidth = document.documentElement.clientWidth;
        const padding = 15; // 距离屏幕边缘的安全距离

        if (left < padding) {
            left = padding; // 靠左时贴住左侧边界
        } else if (left + popupWidth > screenWidth - padding) {
            left = screenWidth - popupWidth - padding; // 靠右时贴住右侧边界
        }

        // 如果文字太靠近顶部，导致弹窗超出屏幕上方，则改到选区下方显示
        if (rect.top - popupHeight - 10 < 0) {
            top = rect.bottom + scrollTop + 10;
        }

        popup.style.left = `${left}px`;
        popup.style.top = `${top}px`;

    } catch (err) {
        popup.style.display = 'none';
    }
}

document.addEventListener('mouseup', function () {
    setTimeout(handleSelection, 100);
});

document.addEventListener('mousedown', function (e) {
    if (!popup.contains(e.target)) {
        popup.style.display = 'none';
    }
});

document.addEventListener('touchend', function () {
    setTimeout(handleSelection, 100);
});
document.addEventListener('touchstart', function (e) {
    if (!popup.contains(e.target)) {
        popup.style.display = 'none';
    }
});

popup.addEventListener('click', function () {
    const origin = window.location.origin;
    const targetUrl = `${origin}/search/?q=${encodeURIComponent(searchText)}`;
    window.open(targetUrl, '_blank');
    popup.style.display = 'none';
    window.getSelection().removeAllRanges();
});