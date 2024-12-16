document.addEventListener('DOMContentLoaded', () => {
    const notificationButton = document.getElementById('notificationButton');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationList = document.getElementById('notificationList');
    const notificationBadge = document.getElementById('notificationBadge');
    let unreadCount = 0;
    let activeConnection = null;
    const RECONNECT_DELAY = 2000;

    fetchNotifications();

    notificationButton.addEventListener('click', () => {
        notificationDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!notificationDropdown.contains(e.target) && 
            !notificationButton.contains(e.target)) {
            notificationDropdown.classList.add('hidden');
        }
    });

    const createNotificationHTML = (notification, csrfToken) => `
        <form method="post" action="/notifications/${notification.id}/read/" 
            class="flex items-center justify-between space-x-4 rounded-lg p-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/80 group">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900 dark:text-slate-100 group-hover:text-slate-900 dark:group-hover:text-slate-100">${notification.message}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 group-hover:text-slate-500 dark:group-hover:text-slate-400">${new Date(notification.created_at).toLocaleString()}</p>
            </div>
            ${!notification.is_read ? `
                <button type="submit" class="inline-flex h-8 w-8 items-center justify-center rounded-full text-emerald-500 hover:bg-emerald-100 hover:text-emerald-600 dark:hover:bg-emerald-900/30">
                    <i class="fa-regular fa-eye"></i>
                </button>
            ` : ''}
        </form>
    `;


    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    const debouncedFetch = debounce(fetchNotifications, 250);

    function fetchNotifications() {
        fetch('/api/notifications/')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                const notifications = data.notifications;
                notificationList.innerHTML = '';
                
                const notificationsArray = Array.from(notifications);
                unreadCount = notificationsArray.filter(n => !n.is_read).length;
                notificationBadge.textContent = unreadCount;
    
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                notificationsArray.forEach(notification => {
                    const notificationItem = document.createElement('div');
                    notificationItem.className = `notification-item border-b border-slate-200 dark:border-slate-700 last:border-0 ${
                        notification.is_read 
                            ? 'bg-white dark:bg-slate-800' 
                            : 'bg-purple-50 dark:bg-purple-900/20'
                    }`;
                    
                    notificationItem.dataset.notificationType = notification.notification_type;
                    
                    if (notification.notification_type === 'leave_request' || 
                        notification.notification_type === 'leave_status') {
                        notificationItem.dataset.leaveUrl = '/employees/leaves/';
                    } else if (notification.notification_type === 'report_status' && notification.report) {
                        notificationItem.dataset.reportUrl = `/reports/${notification.report}/update/`;
                    } else if (notification.notification_type === 'registration') {
                        notificationItem.dataset.registrationUrl = '/employees/inactive/';
                    }
                
                    notificationItem.innerHTML = createNotificationHTML(notification, csrfToken);
                    notificationList.appendChild(notificationItem);
                });
    
                addNotificationClickHandlers();
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
                notificationList.innerHTML = '<div class="p-4 text-sm text-red-500 dark:text-red-400">Failed to load notifications</div>';
            });
    }

    function addNotificationClickHandlers() {
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    const type = item.dataset.notificationType;
                    if (type === 'report_status') {
                        window.location.href = item.dataset.reportUrl;
                    } else if (type === 'registration') {
                        window.location.href = item.dataset.registrationUrl;
                    } else if (type === 'leave_status') {
                        window.location.href = item.dataset.leaveUrl;
                    }
                }
            });
        });
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed z-50 flex items-center p-4 bg-white rounded-lg shadow-lg bottom-5 right-5 dark:bg-slate-800';
        toast.innerHTML = `
            <div class="mr-3 inline-flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-purple-100 text-purple-500 dark:bg-purple-900 dark:text-purple-300">
                <i class="fa-solid fa-bell"></i>
            </div>
            <div class="text-sm font-normal text-slate-900 dark:text-slate-100">${message}</div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('opacity-0', 'transition-opacity');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    function initializeWebSocket() {
        if (activeConnection) {
            activeConnection.close();
            activeConnection = null;
        }
    
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        
        try {
            activeConnection = new WebSocket(`${wsProtocol}//${window.location.host}/ws/notifications/`);
    
            activeConnection.onopen = function() {
                // console.log('WebSocket connected');
            };
    
            activeConnection.onmessage = function(e) {
                const data = JSON.parse(e.data);
                debouncedFetch();
                showToast(data.message);
            };
    
            activeConnection.onclose = function(event) {
                if (event.wasClean) {
                    setTimeout(() => {
                        if (document.visibilityState === 'visible') {
                            initializeWebSocket();
                        }
                    }, RECONNECT_DELAY);
                }
            };
        } catch (error) {
            console.debug('WebSocket connection handled');
        }
    }

    window.addEventListener('beforeunload', () => {
        if (activeConnection) {
            activeConnection.close(1000, 'Page navigation');
        }
    });
    
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            initializeWebSocket();
        }
    });

    window.addEventListener('load', initializeWebSocket);
});
