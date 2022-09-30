import websocket, json, threading
import threading

class GcsWebsocketClient:
    """
    GCS Client Interface

    """

    def __init__(self, api_url="ws://localhost:8000/ws/robot/guy/", headers={'X-DroneApiKey':"hOgtypH7.eQM8nQbEUNyQY5gPUQg0IG1WbuopENfz"}):
        #websocket.enableTrace(True)
        ws = websocket.WebSocket()
        ws.connect(api_url,
					header=headers,
                    )
        self.ws = ws
        #self.ws.on_open = self.on_open
        #self.ws.run_forever()

    def send_telemetry(self, message=None):
        message = json.dumps({ 'message' : message })
        self.ws.send('%s' % message)


