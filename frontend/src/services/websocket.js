
const WS_URL =
  import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8001/ws";

let socket = null;
let disconnectTimer = null;
let activeHandlers = null;

export function connectToPacketStream(onPacket, onStatusChange) {
  // Cancel a pending disconnect if the dashboard mounts again.
  if (disconnectTimer !== null) {
    clearTimeout(disconnectTimer);
    disconnectTimer = null;
  }

  activeHandlers = { onPacket, onStatusChange };

  // Reuse a connection that is already opening or open.
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    return socket;
  }

  const currentSocket = new WebSocket(WS_URL);
  socket = currentSocket;

  currentSocket.onopen = () => {
    if (socket !== currentSocket) return;
    console.log("Connected to Cogni-Fi packet stream");
    activeHandlers?.onStatusChange?.("connected");
  };

  currentSocket.onmessage = (event) => {
    if (socket !== currentSocket) return;

    try {
      const packet = JSON.parse(event.data);
      activeHandlers?.onPacket?.(packet);
    } catch (error) {
      console.error("Invalid WebSocket message:", error);
    }
  };

  currentSocket.onerror = (error) => {
    if (socket !== currentSocket) return;
    console.error("Cogni-Fi WebSocket error:", error);
    activeHandlers?.onStatusChange?.("error");
  };

  currentSocket.onclose = (event) => {
    console.log(
      `Cogni-Fi WebSocket closed. Code: ${event.code}, ` +
        `Reason: ${event.reason || "No reason provided"}, ` +
        `Clean: ${event.wasClean}`
    );

    if (socket === currentSocket) {
      socket = null;
      activeHandlers?.onStatusChange?.("disconnected");
    }
  };

  return currentSocket;
}

export function disconnectFromPacketStream() {
  if (disconnectTimer !== null) {
    clearTimeout(disconnectTimer);
  }

  // Allow an immediate Strict Mode remount to reuse the connection.
  disconnectTimer = setTimeout(() => {
    disconnectTimer = null;

    const currentSocket = socket;
    socket = null;
    activeHandlers = null;

    if (
      currentSocket &&
      (currentSocket.readyState === WebSocket.CONNECTING ||
        currentSocket.readyState === WebSocket.OPEN)
    ) {
      currentSocket.close(1000, "Dashboard disconnected");
    }
  }, 250);
}
