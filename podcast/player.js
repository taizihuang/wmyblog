function addButton(ap){
        ap.on('canplay', function () {
            // 防止重複插入按鈕
            if (document.querySelector('.aplayer-icon-forward10')) return;

            // 找到 APlayer 的控制列容器（通常在音量按鈕或時間顯示附近）
            const barWrap = document.querySelector('.aplayer-time');
            const volumeBtn = document.querySelector('.aplayer-volume-wrap');
            
            if (barWrap) {
                // 建立按鈕的 DOM 節點
                const forwardBtn = document.createElement('button');
                forwardBtn.type = 'button';
                forwardBtn.className = 'aplayer-icon aplayer-icon-forward10';
                forwardBtn.title = '快进 10 秒';
                forwardBtn.setAttribute('aria-label', 'Rewind 10 seconds');
                forwardBtn.innerHTML = `
                <svg width="16px" height="16px" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0.790619 2.09314C0.638212 1.98427 0.437745 1.96972 0.271209 2.05542C0.104674 2.14112 0 2.31271 0 2.5V12.5C0 12.6873 0.104674 12.8589 0.271209 12.9446C0.437745 13.0303 0.638212 13.0157 0.790619 12.9069L7 8.4716V12.5C7 12.6873 7.10467 12.8589 7.27121 12.9446C7.43774 13.0303 7.63821 13.0157 7.79062 12.9069L14.7906 7.90687C14.922 7.81301 15 7.66148 15 7.5C15 7.33853 14.922 7.18699 14.7906 7.09314L7.79062 2.09314C7.63821 1.98427 7.43774 1.96972 7.27121 2.05542C7.10467 2.14112 7 2.31271 7 2.5V6.52841L0.790619 2.09314Z" fill="#000000"/>
                </svg>
                `;

                const rewindBtn = document.createElement('button');
                rewindBtn.type = 'button';
                rewindBtn.className = 'aplayer-icon aplayer-icon-rewind';
                rewindBtn.title = '快退 10 秒';
                rewindBtn.setAttribute('aria-label', 'Rewind 10 seconds');
                rewindBtn.innerHTML = `
                <svg width="8px" height="8px" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 2.5C8 2.31271 7.89533 2.14112 7.72879 2.05542C7.56226 1.96972 7.36179 1.98427 7.20938 2.09314L0.209381 7.09314C0.0779829 7.18699 0 7.33853 0 7.5C0 7.66148 0.0779829 7.81301 0.209381 7.90687L7.20938 12.9069C7.36179 13.0157 7.56226 13.0303 7.72879 12.9446C7.89533 12.8589 8 12.6873 8 12.5V8.4716L14.2094 12.9069C14.3618 13.0157 14.5623 13.0303 14.7288 12.9446C14.8953 12.8589 15 12.6873 15 12.5V2.5C15 2.31271 14.8953 2.14112 14.7288 2.05542C14.5623 1.96972 14.3618 1.98427 14.2094 2.09314L8 6.52841V2.5Z" fill="#000000"/>
                </svg>
                `;
                
                // 將按鈕插入到時間顯示的後方
                barWrap.insertBefore(rewindBtn, volumeBtn);
                barWrap.appendChild(forwardBtn);

                // 3. 綁定點擊事件，實現快進 10 秒
                forwardBtn.addEventListener('click', function (e) {
                    e.stopPropagation(); // 阻止事件冒泡
                    
                    if (ap.audio) {
                        const currentTime = ap.audio.currentTime;
                        const duration = ap.audio.duration;
                        
                        // 計算快進後的時間，確保不超過總長度
                        let newTime = currentTime + 10;
                        if (newTime > duration) {
                            newTime = duration;
                        }
                        
                        // 設定新時間並讓播放器跳轉（seek）
                        ap.seek(newTime);
                    }
                });

                rewindBtn.addEventListener('click', (e) => {
                    e.stopPropagation(); // 阻止事件冒泡
                    
                    if (ap.audio) {
                        const currentTime = ap.audio.currentTime;
                        
                        let newTime = currentTime - 10;
                        if (newTime < 0) {
                            newTime = 0;
                        }
                        
                        ap.seek(newTime);
                    }
                });
            }
        });
    }

    function keyevent(ap, document) {
        const SKIP_TIME = 10;
        document.addEventListener('keydown', (event) => {
            const activeEl = document.activeElement;
            const isInputting = activeEl && (
                ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeEl.tagName) ||
                activeEl.isContentEditable
            );
            if (isInputting) {
                return;
            }

            if (!ap || !ap.audio) {
                return;
            }

            switch (event.code) {
                case 'Space':
                    event.preventDefault(); // 阻止页面向下滚动的默认行为
                    ap.toggle();            // 调用 APlayer 原生的播放/暂停切换方法
                    break;
                case 'ArrowLeft':
                    event.preventDefault(); // 阻止页面向左滚动的默认行为
                    ap.audio.currentTime = Math.max(0, ap.audio.currentTime - SKIP_TIME);
                    break;
                case 'ArrowRight':
                    event.preventDefault(); // 阻止页面向右滚动的默认行为
                    ap.audio.currentTime = Math.min( ap.audio.duration || Infinity, ap.audio.currentTime + SKIP_TIME);
                    break;
                default:
                    break;
            }
        });
    }