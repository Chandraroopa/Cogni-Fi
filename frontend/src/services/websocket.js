
const WS_URL =
  import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8001/ws";

const RECONNECT_DELAY = 2000;
const MAX_RECONNECT_DELAY = 10000;
const DISCONNECT_DELAY = 250;

let socket = null;
let disconnectTimer = null;
let reconnectTimer = null;
let activeHandlers = null;
let reconnectAttempts = 0;
let manuallyDisconnected = false;

function notifyStatus(status) {
  activeHandlers?.onStatusChange?.(status);
}

function clearReconnectTimer() {
  if (reconnectTimer !== null) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
}

function scheduleReconnect() {
  if (manuallyDisconnected || !activeHandlers || reconnectTimer !== null) {
    return;
  }

  const delay = Math.min(
    RECONNECT_DELAY * Math.pow(2, reconnectAttempts),
    MAX_RECONNECT_DELAY
  );

  reconnectAttempts += 1;

  console.log(`[Cogni-Fi] Reconnecting in ${delay / 1000}s...`);
  notifyStatus("reconnecting");

  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;

    if (!manuallyDisconnected && activeHandlers) {
      openSocket();
    }
  }, delay);
}

function openSocket() {
  if (manuallyDisconnected || !activeHandlers) return null;

  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    return socket;
  }

  clearReconnectTimer();

  let currentSocket;

  try {
    currentSocket = new WebSocket(WS_URL);
  } catch (error) {
    console.error("[Cogni-Fi] WebSocket creation failed:", error);
    notifyStatus("error");
    scheduleReconnect();
    return null;
  }

  socket = currentSocket;
  notifyStatus("connecting");

  currentSocket.onopen = () => {
    if (socket !== currentSocket) return;

    reconnectAttempts = 0;

    console.log("[Cogni-Fi] Connected to packet stream:", WS_URL);
    notifyStatus("connected");
  };

  currentSocket.onmessage = (event) => {
    if (socket !== currentSocket) return;

    try {
      const message = JSON.parse(event.data);

      // The backend currently sends risk_update messages containing
      // window features, ML results, and risk assessment.
      console.log("[Cogni-Fi] Received:", message);

      activeHandlers?.onPacket?.(message);
    } catch (error) {
      console.error("[Cogni-Fi] Invalid WebSocket message:", error);
      console.error("[Cogni-Fi] Raw message:", event.data);
    }
  };

  currentSocket.onerror = (error) => {
    if (socket !== currentSocket) return;

    console.error("[Cogni-Fi] WebSocket error:", error);
    notifyStatus("error");
  };

  currentSocket.onclose = (event) => {
    console.log(
      `[Cogni-Fi] WebSocket closed. Code: ${event.code}, ` +
        `Reason: ${event.reason || "No reason provided"}, ` +
        `Clean: ${event.wasClean}`
    );

    if (socket !== currentSocket) return;

    socket = null;

    if (!manuallyDisconnected && activeHandlers) {
      scheduleReconnect();
    } else {
      notifyStatus("disconnected");
    }
  };

  return currentSocket;
}

export function connectToPacketStream(onPacket, onStatusChange) {
  manuallyDisconnected = false;

  if (disconnectTimer !== null) {
    clearTimeout(disconnectTimer);
    disconnectTimer = null;
  }

  activeHandlers = { onPacket, onStatusChange };

  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    return socket;
  }

  return openSocket();
}

export function disconnectFromPacketStream() {
  if (disconnectTimer !== null) {
    clearTimeout(disconnectTimer);
  }

  // Delay cleanup so React Strict Mode can immediately remount.
  disconnectTimer = setTimeout(() => {
    disconnectTimer = null;
    manuallyDisconnected = true;

    clearReconnectTimer();

    const currentSocket = socket;

    socket = null;

    if (
      currentSocket &&
      (currentSocket.readyState === WebSocket.CONNECTING ||
        currentSocket.readyState === WebSocket.OPEN)
    ) {
      currentSocket.close(1000, "Dashboard disconnected");
    }

    activeHandlers = null;
    reconnectAttempts = 0;
  }, DISCONNECT_DELAY);
}
