let ws = null;
let notificationWs = null;
const clients = new Set();
let notificationCount = 0;
const MAX_RETRY_ATTEMPTS = 3;
let retryCount = 0;

function createWebSockets() {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    
    const protocol = self.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = self.location.host;
    
    try {
        ws = new WebSocket(`${protocol}//${host}/ws/user_activity/`);
        notificationWs = new WebSocket(`${protocol}//${host}/ws/notifications/`);
        
        ws.onmessage = (event) => {
            clients.forEach(client => client.postMessage({type: 'activity', data: event.data}));
        };
        
        notificationWs.onmessage = (event) => {
            clients.forEach(client => client.postMessage({type: 'notification', data: event.data}));
        };
        
        ws.onopen = notificationWs.onopen = () => {
            retryCount = 0;
        };
        
        ws.onclose = notificationWs.onclose = () => {
            if (retryCount < MAX_RETRY_ATTEMPTS) {
                retryCount++;
                setTimeout(createWebSockets, 1000 * retryCount);
            }
        };
    } catch (error) {
        console.debug('WebSocket connection handled');
    }
}

self.onconnect = (e) => {
    const port = e.ports[0];
    clients.add(port);
    
    if (!ws || ws.readyState === WebSocket.CLOSED) {
        createWebSockets();
    }
    
    port.start();
    port.postMessage({type: 'notificationCount', count: notificationCount});
};
