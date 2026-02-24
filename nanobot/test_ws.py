import asyncio
import websockets
import sys

async def test_nanobot():
    uri = "ws://127.0.0.1:8888/ws"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Type a message and press Enter (or 'quit' to exit):")
            
            # Start a background task to continuously listen for incoming messages
            async def receive_messages():
                try:
                    while True:
                        response = await websocket.recv()
                        # Print response on a new line, then reprint the prompt
                        print(f"\n[Nanobot]:\n{response}\n> ", end="", flush=True)
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed by server.")
                except asyncio.CancelledError:
                    pass
            
            receive_task = asyncio.create_task(receive_messages())
            
            # Main loop to read input from terminal and send messages
            while True:
                # Use to_thread to prevent input() from blocking the asyncio event loop
                message = await asyncio.to_thread(input, "> ")
                
                if message.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if message.strip():
                    await websocket.send(message)
            
            receive_task.cancel()
            
    except ConnectionRefusedError:
        print(f"\nError: Connection refused. Is Nanobot gateway running on port 8888?")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    # Ensure websockets is installed (it is in pyproject.toml)
    try:
        asyncio.run(test_nanobot())
    except KeyboardInterrupt:
        print("\nExiting...")
