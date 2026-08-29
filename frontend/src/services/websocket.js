const WS_URL = "ws://127.0.0.1:8000/ws";

let socket = null;

export function connectToPacketStream(onPacket, onStatusChange) {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("Connected to Cognifi packet stream");
        onStatusChange?.("connected");
    };

    socket.onmessage = (event) => {
        try {
            const packet = JSON.parse(event.data);
            onPacket?.(packet);
        } catch (error) {
            console.error("Invalid packet received:", error);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        onStatusChange?.("error");
    };

    socket.onclose = () => {
        console.log("Packet stream disconnected");
        onStatusChange?.("disconnected");
    };

    return socket;
}

export function disconnectFromPacketStream() {
    if (socket) {
        socket.close();
        socket = null;
    }
}