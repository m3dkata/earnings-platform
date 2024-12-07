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
        <form method="post" action="/notifications/${notification.id}/read/" class="flex justify-between items-start">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <div>
                <p class="text-xs dark:text-white">${notification.message}</p>
                <small class="text-xs text-slate-500 dark:text-white">${new Date(notification.created_at).toLocaleString()}</small>
            </div>
            ${!notification.is_read ? `
                <button type="submit" class="text-lime-500 hover:text-lime-600">
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
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
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
                    notificationItem.className = `notification-item p-2 cursor-pointer ${
                        notification.is_read ? 'bg-slate-100 dark:bg-slate-700' : 'bg-purple-400 dark:bg-slate-800'
                    } border-b border-slate-200`;
                    
                    notificationItem.dataset.notificationType = notification.notification_type;
                    if (notification.notification_type === 'report_status' && notification.report) {
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
                notificationList.innerHTML = '<div class="p-2 text-red-500">Failed to load notifications</div>';
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
                    }
                }
            });
        });
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-5 right-5 bg-white dark:bg-slate-700 p-4 rounded-lg shadow-lg z-50';
        toast.innerHTML = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
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
