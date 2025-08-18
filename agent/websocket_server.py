# ABOUTME: WebSocket server for agent-to-frontend communication
# ABOUTME: Receives view intents from agent and broadcasts to connected frontend clients
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connected_clients = set()


async def handle_client(websocket):
    """Handle a new WebSocket client connection."""
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")

    try:
        await websocket.wait_closed()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")


async def broadcast_intent(intent_data):
    """Broadcast an intent to all connected clients."""
    if not connected_clients:
        logger.warning("No clients connected to broadcast intent")
        return

    message = json.dumps(intent_data)
    logger.info(f"Broadcasting intent to {len(connected_clients)} clients: {message}")

    disconnected = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.add(client)

    for client in disconnected:
        connected_clients.discard(client)


async def start_server():
    """Start the WebSocket server."""
    logger.info("Starting WebSocket server on localhost:8765")
    server = await websockets.serve(handle_client, "localhost", 8765)
    return server


if __name__ == "__main__":

    async def main():
        server = await start_server()
        logger.info("WebSocket server started")
        await server.wait_closed()

    asyncio.run(main())
