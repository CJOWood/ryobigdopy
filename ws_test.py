import websockets
import asyncio

class WebSocketClient():

    def __init__(self):
        pass

    async def connect(self):
        '''
            Connecting to webSocket server

            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        self.connection = await websockets.connect('wss://ws.postman-echo.com/raw')
        if self.connection.open:
            print('Connection stablished. Client correcly connected')
            # Send greeting
            await self.sendMessage('Hey server, this is webSocket client')
            return self.connection


    async def sendMessage(self, message):
        '''
            Sending message to webSocket server
        '''
        await self.connection.send(message)

    async def receiveMessage(self, connection):
        '''
            Receiving all server messages and handling them
        '''
        while True:
            try:
                message = await connection.recv()
                print('Received message from server: ' + str(message))
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def heartbeat(self, connection):
        '''
        Sending heartbeat to server every 5 seconds
        Ping - pong messages to verify connection is alive
        '''
        while True:
            try:
                await connection.send('ping')
                await asyncio.sleep(5)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break
