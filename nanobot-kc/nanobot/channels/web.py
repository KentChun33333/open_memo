"""Web channel implementation using FastAPI and WebSockets."""

import asyncio
import json
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger

from nanobot.bus.events import InboundMessage, OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import WebConfig


class WebChannel(BaseChannel):
    """Web channel using FastAPI and WebSockets."""
    
    name = "web"
    
    def __init__(self, config: WebConfig, bus: MessageBus):
        super().__init__(config, bus)
        self.config: WebConfig = config
        self.app = FastAPI(title="Nanobot Web Channel")
        self.active_connections: list[WebSocket] = []
        self._server: uvicorn.Server | None = None
        
        self._setup_routes()

    def _setup_routes(self):
        @self.app.websocket(self.config.path)
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            client_id = f"web_{id(websocket)}"
            logger.info(f"New web connection: {client_id}")
            
            try:
                while True:
                    data = await websocket.receive_text()
                    
                    # Create InboundMessage and send to the agent bus
                    msg = InboundMessage(
                        channel="web",
                        chat_id=client_id,
                        sender_id=client_id,
                        content=data.strip()
                    )
                    await self.bus.publish_inbound(msg)
                    
            except WebSocketDisconnect:
                logger.info(f"Web connection closed: {client_id}")
                self.active_connections.remove(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)

    async def start(self) -> None:
        """Start the FastAPI server via Uvicorn."""
        if not self.config.enabled:
            return
            
        logger.info(f"Starting Web channel on ws://{self.config.host}:{self.config.port}{self.config.path}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="error" # Suppress uvicorn info logs to keep nanobot logs clean
        )
        self._server = uvicorn.Server(config)
        
        # We use asyncio.create_task so the server runs in the background and start_all doesn't block forever
        asyncio.create_task(self._server.serve())

    async def stop(self) -> None:
        """Stop the Web channel."""
        logger.info("Stopping Web channel...")
        if self._server:
            self._server.should_exit = True
            await self._server.shutdown()
        # Close all active web sockets
        for ws in self.active_connections:
            await ws.close()
        self.active_connections.clear()

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message to all active WebSocket connections."""
        for ws in self.active_connections:
            try:
                # We can optionally filter by chat_id if we want to target a specific tab
                # if msg.chat_id == f"web_{id(ws)}":
                await ws.send_text(msg.content)
            except Exception as e:
                logger.error(f"Error sending message to web client: {e}")
