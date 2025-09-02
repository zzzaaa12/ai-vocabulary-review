/**
 * 統一的通知系統
 * 替代原生 alert、confirm 等彈出框
 * 使用 Bootstrap Toast 和 Modal 組件
 */

class NotificationSystem {
    constructor() {
        this.init();
    }

    init() {
        // 創建 Toast 容器
        this.createToastContainer();
        // 創建通用確認 Modal
        this.createConfirmModal();
    }

    /**
     * 創建 Toast 容器
     */
    createToastContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
        }
    }

    /**
     * 創建通用確認 Modal
     */
    createConfirmModal() {
        if (!document.getElementById('universal-confirm-modal')) {
            const modalHtml = `
                <div class="modal fade" id="universal-confirm-modal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="confirm-modal-title">
                                    <i class="bi bi-question-circle"></i> 確認操作
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p id="confirm-modal-message">您確定要執行此操作嗎？</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                <button type="button" class="btn btn-primary" id="confirm-modal-ok">確認</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
    }

    /**
     * 顯示 Toast 通知
     * @param {string} message - 訊息內容
     * @param {string} type - 類型 (success, error, warning, info)
     * @param {number} duration - 顯示時間（毫秒）
     */
    showToast(message, type = 'info', duration = 4000) {
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };

        const bgColorMap = {
            success: 'bg-success',
            error: 'bg-danger',
            warning: 'bg-warning',
            info: 'bg-info'
        };

        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgColorMap[type]} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi bi-${iconMap[type]} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        const container = document.getElementById('toast-container');
        container.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });

        toast.show();

        // 自動清理 DOM
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        return toast;
    }

    /**
     * 顯示成功通知
     */
    success(message, duration = 3000) {
        return this.showToast(message, 'success', duration);
    }

    /**
     * 顯示錯誤通知
     */
    error(message, duration = 5000) {
        return this.showToast(message, 'error', duration);
    }

    /**
     * 顯示警告通知
     */
    warning(message, duration = 4000) {
        return this.showToast(message, 'warning', duration);
    }

    /**
     * 顯示資訊通知
     */
    info(message, duration = 3000) {
        return this.showToast(message, 'info', duration);
    }

    /**
     * 顯示確認對話框
     * @param {string} message - 確認訊息
     * @param {string} title - 對話框標題
     * @param {Object} options - 選項 {okText, cancelText, okClass}
     * @returns {Promise<boolean>} - 用戶選擇結果
     */
    confirm(message, title = '確認操作', options = {}) {
        return new Promise((resolve) => {
            const modal = document.getElementById('universal-confirm-modal');
            const titleElement = document.getElementById('confirm-modal-title');
            const messageElement = document.getElementById('confirm-modal-message');
            const okButton = document.getElementById('confirm-modal-ok');

            // 設置內容
            titleElement.innerHTML = `<i class="bi bi-question-circle"></i> ${title}`;
            messageElement.textContent = message;

            // 設置按鈕文字和樣式
            okButton.textContent = options.okText || '確認';
            okButton.className = `btn ${options.okClass || 'btn-primary'}`;

            // 綁定事件
            const handleConfirm = () => {
                cleanup();
                resolve(true);
            };

            const handleCancel = () => {
                cleanup();
                resolve(false);
            };

            const cleanup = () => {
                okButton.removeEventListener('click', handleConfirm);
                modal.removeEventListener('hidden.bs.modal', handleCancel);
                bootstrap.Modal.getInstance(modal).hide();
            };

            okButton.addEventListener('click', handleConfirm);
            modal.addEventListener('hidden.bs.modal', handleCancel, { once: true });

            // 顯示 Modal
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        });
    }

    /**
     * 顯示危險操作確認框
     */
    confirmDanger(message, title = '危險操作') {
        return this.confirm(message, title, {
            okText: '確認刪除',
            okClass: 'btn-danger'
        });
    }

    /**
     * 顯示載入中通知
     * @param {string} message - 載入訊息
     * @returns {Object} - 包含 hide 方法的對象
     */
    loading(message = '載入中...') {
        const toast = this.showToast(
            `<span class="spinner-border spinner-border-sm me-2"></span>${message}`,
            'info',
            0 // 不自動隱藏
        );

        return {
            hide: () => {
                const toastElement = toast._element;
                if (toastElement) {
                    toast.hide();
                }
            }
        };
    }
}

// 創建全局實例
window.notify = new NotificationSystem();

// 提供簡化的全局函數
window.showToast = (message, type, duration) => notify.showToast(message, type, duration);
window.showSuccess = (message, duration) => notify.success(message, duration);
window.showError = (message, duration) => notify.error(message, duration);
window.showWarning = (message, duration) => notify.warning(message, duration);
window.showInfo = (message, duration) => notify.info(message, duration);
window.showConfirm = (message, title, options) => notify.confirm(message, title, options);
window.showLoading = (message) => notify.loading(message);

// 替代原生 alert 和 confirm
window.alert = (message) => {
    console.warn('使用了原生 alert，建議改用 showInfo 或 showError');
    return notify.info(message);
};

window.confirm = (message) => {
    console.warn('使用了原生 confirm，建議改用 showConfirm');
    return notify.confirm(message);
};
