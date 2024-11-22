import time
import math
import threading
from flask import Flask, request, jsonify
from rpi_ws281x import PixelStrip, Color

# LED-konfiguration
LED_COUNT = 60
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# Initiera LED-stripen
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Flask-app
app = Flask(__name__)

# Laddar lösenord från fil
with open('password.txt', 'r') as f:
    PASSWORD = f.read().strip()

# Trådhantering för effekter
current_thread = None
stop_event = threading.Event()

# Stäng av alla LED
def stop_effects():
    global stop_event
    stop_event.set()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# Rullande vågeffekt
def rollingWave(direction='forward', wave_length=10, speed=0.1, color=(0, 0, 255)):
    global stop_event
    stop_event.clear()
    step_range = range(strip.numPixels()) if direction == 'forward' else range(strip.numPixels() - 1, -1, -1)
    while not stop_event.is_set():
        for step in step_range:
            for i in range(strip.numPixels()):
                intensity = (math.sin(2 * math.pi * (i + step) / wave_length) + 1) / 2
                adjusted_color = Color(
                    int(color[0] * intensity),
                    int(color[1] * intensity),
                    int(color[2] * intensity)
                )
                strip.setPixelColor(i, adjusted_color)
            strip.show()
            time.sleep(speed)
            if stop_event.is_set():
                break

# Blinkande effekt
def blink_effect(color=(255, 0, 0), speed=1):
    global stop_event
    stop_event.clear()
    while not stop_event.is_set():
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(color[0], color[1], color[2]))
        strip.show()
        time.sleep(speed)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(speed)

# Startar en ny tråd för effekten
def start_effect(effect_function, *args, **kwargs):
    global current_thread
    global stop_event
    if current_thread and current_thread.is_alive():
        stop_event.set()
        current_thread.join()
    stop_event.clear()
    current_thread = threading.Thread(target=effect_function, args=args, kwargs=kwargs)
    current_thread.start()

# Färghantering
def get_color(color_name):
    if color_name == 'blue':
        return (0, 0, 255)
    elif color_name == 'green':
        return (0, 255, 0)
    elif color_name == 'red':
        return (255, 0, 0)
    else:
        return (255, 255, 255)

# Autentisering
def authenticate(data):
    if 'password' not in data or data['password'] != PASSWORD:
        return False
    return True

# API-endpoints
@app.route('/stop_effects', methods=['POST'])
def api_stop_effects():
    data = request.json
    if not authenticate(data):
        return jsonify({"error": "Unauthorized"}), 401
    stop_effects()
    return jsonify({"status": "stopped"})

@app.route('/set_wave', methods=['POST'])
def api_set_wave():
    data = request.json
    if not authenticate(data):
        return jsonify({"error": "Unauthorized"}), 401
    direction = data.get('direction', 'forward')
    color = data.get('color', 'blue')
    wave_color = get_color(color)
    start_effect(rollingWave, direction=direction, wave_length=10, speed=0.1, color=wave_color)
    return jsonify({"status": "wave started", "direction": direction, "color": color})

@app.route('/set_blink', methods=['POST'])
def api_set_blink():
    data = request.json
    if not authenticate(data):
        return jsonify({"error": "Unauthorized"}), 401
    color = data.get('color', 'red')
    speed = data.get('speed', 1)
    blink_color = get_color(color)
    start_effect(blink_effect, color=blink_color, speed=speed)
    return jsonify({"status": "blink started", "color": color, "speed": speed})

@app.route('/status', methods=['GET'])
def api_status():
    status = "running" if current_thread and current_thread.is_alive() else "stopped"
    return jsonify({"status": status})

# Starta Flask-servern
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

