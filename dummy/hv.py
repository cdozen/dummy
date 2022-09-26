import paho.mqtt.client as mqtt
from dataclasses import dataclass
import time
import json

from typing import Union


@dataclass
class Channel(object):
    number: int
    on: bool = False
    vreq: float = 0.0


class DummyHV(object):
    def __init__(self, name: str, n_channels: int = 1):
        self.channels = [Channel(i) for i in range(n_channels)]
        self.name = name

    def command(self, topic: str, message: Union[bytes, float, int]) -> None:
        device, cmd, command, channel = topic.split("/")[1:]
        if cmd != "cmd":
            raise ValueError("command messages should be of the form /device/cmd/#")
        commands = ["switch", "setv"]
        if device != self.name:
            raise ValueError("wrong hv! ", device, self.name)
        channel = int(channel)
        if command == "switch":
            message = message.decode("utf-8")
            if message == "on":
                self.channels[channel].on = True
            elif message == "off":
                self.channels[channel].on = False
            else:
                msg = "can only switch on or off"
                raise ValueError(msg)
        elif command == "setv":
            self.channels[channel].vreq = float(message)
        else:
            raise ValueError("only possible commands are", commands)

    def status(self):
        """TODO: Write unittest"""
        status_channels = []
        for channel in self.channels:
            status_channels.append(
                {
                    "number": channel.number,
                    "on": int(channel.on),  # issue with bools in telegraf/influxdb
                    "vreq": channel.vreq,
                }
            )
        return status_channels


def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"/{client.device.name}/cmd/#")


def on_message(client, userdata, msg):
    print("recv", msg.topic, msg.payload)
    client.device.command(msg.topic, msg.payload)


def run(device, mqtt_host):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
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
    device = DummyHV(device_name)
    run(device, mqtt_host)
