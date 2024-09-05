import asyncio
import websockets
import base64
import serial
import json
from picamera2 import Picamera2
from PIL import Image
from io import BytesIO
import numpy as np
import time
import datetime

# Initialize serial communication
ser = serial.Serial('/dev/ttyACM0', 9600)
picam2 = Picamera2()
#picam2.preview_configuration.main.size = (1920, 1080)  # full screen : 3280 2464
picam2.preview_configuration.main.format = "RGB888"  # 8 bits
picam2.start()

async def video_stream(websocket, path):
    try:
        while True:
            try:
                image_pil = picam2.capture_image()

                #image_pil = Image.open(path)
                cap = np.array(image_pil)
            except Exception as e:
                print(f"Error capturing image: {e}")
                continue  # Skip this iteration if capturing fails

            try:
                # Read data from the serial port
                 if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    serial_data = [int(x) for x in line.split(',')]
                 else:
                    serial_data = serial_data
            except Exception as e:
                print(f"Error reading serial data: {e}")
                serial_data = [0, 0]  # Use default values on error

            try:
                # Encode the frame in JPEG format
                pil_img = Image.fromarray(cap)
                buff = BytesIO()
                pil_img.save(buff, format="JPEG")
                new_image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
            except Exception as e:
                print(f"Error encoding image: {e}")
                continue  # Skip this iteration if encoding fails

            try:
                # Create a JSON object with both the frame and the serial data
                now =datetime.datetime.now()
                time_now = now.strftime('%D %H:%M:%S')
                print(time_now)
                message = json.dumps({
                    'frame': new_image_string,
                    'HUM': serial_data[0],
                    'lx': serial_data[1],
                    'time': time_now
                })

                # Send the message to the client
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed: Normal closure")
                break  # Exit the loop if the connection is closed normally
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Connection closed with error: {e}")
                break  # Exit the loop if the connection is closed with an error
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue  # Skip this iteration on unexpected errors

            await asyncio.sleep(1)  # Adjust the frame interval
    except Exception as e:
        print(f"Critical error in video stream handler: {e}")
    finally:
        print("Cleaning up resources")

async def main():
    while True:
        try:
            async with websockets.serve(video_stream, "192.168.0.118", 8765):
                await asyncio.Future()  # Keep the server running
        except Exception as e:
            print(f"Server error: {e}")
            await asyncio.sleep(1)  # Wait before retrying

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running server: {e}")

