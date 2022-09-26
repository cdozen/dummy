import paho.mqtt.client as mqtt
import time
import json
import math


class Sensor(object):
    def __init__(self, name, func=lambda x: math.sin(x / 5.0)):
        self.name = name
        self.func = func

    def status(self, t=None):
        if t is None:
            t = time.time()
        m1 = self.func(t)
        m2 = math.fabs(m1)
        return {"meas1": m1, "meas2": m2}


def run(device, mqtt_host):
    client = mqtt.Client()
    client.device = device
    client.connect(mqtt_host, 1883, 60)
    client.loop_start()
    while 1:
        client.publish("/{}/status".format(device.name), json.dumps(device.status()))
        time.sleep(1)
    time.sleep(1)
    client.disconnect()
    client.loop_stop()


if __name__ == "__main__":
    import sys

    device_name, mqtt_host = sys.argv[1:]
    device = Sensor(device_name)
    run(device, mqtt_host)
