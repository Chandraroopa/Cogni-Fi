const WS_URL = "ws://127.0.0.1:8000/ws";

let socket = null;

export function connectToPacketStream(onPacket, onStatusChange) {
    if (
        socket &&
        (socket.readyState === WebSocket.CONNECTING ||
            socket.readyState === WebSocket.OPEN)
    ) {
        return socket;
    }

    const currentSocket = new WebSocket(WS_URL);
    socket = currentSocket;

    currentSocket.onopen = () => {
        console.log("Connected to Cognifi packet stream");
        onStatusChange?.("connected");
    };

    currentSocket.onmessage = (event) => {
        try {
            const packet = JSON.parse(event.data);
            onPacket?.(packet);
        } catch (error) {
            console.error("Invalid packet received:", error);
        }
    };

    currentSocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        onStatusChange?.("error");
    };

    currentSocket.onclose = () => {
        console.log("Packet stream disconnected");

        if (socket === currentSocket) {
            socket = null;
        }

        onStatusChange?.("disconnected");
    };

    return currentSocket;
}

export function disconnectFromPacketStream() {
    const currentSocket = socket;
    socket = null;

    if (currentSocket) {
        currentSocket.close();
    }
}