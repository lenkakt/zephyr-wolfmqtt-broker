# wolfMQTT broker on Zephyr

Runs the [wolfMQTT](https://github.com/wolfSSL/wolfMQTT) broker on Zephyr, for the Internet of Things course demo. wolfMQTT is not part of this repository, and this is not an official wolfSSL project.

Status: tested on `native_sim` and on an M5Stack Fire over Wi-Fi, with 10 clients. The XIAO ESP32-C6 build compiles but hasn't been tested.

## Versions

- Zephyr 4.4.2
- wolfMQTT v2.2.0

## Get the code

West downloads Zephyr and wolfMQTT at the right versions. Start in a new, empty folder:

```sh
mkdir broker-workspace && cd broker-workspace
git clone <this repo> zephyr-wolfmqtt-broker
west init -l zephyr-wolfmqtt-broker
west update
west blobs fetch hal_espressif
```

This needs about 2.4 GB, and the Zephyr SDK and Python requirements must already be installed.

## Build and run on Linux

From the workspace:

```sh
west build -p always -b native_sim/native/64 -d build-sim zephyr-wolfmqtt-broker
build-sim/zephyr/zephyr.exe
```

The broker listens on port 1883 of the Linux computer. To test it:

```sh
pip install paho-mqtt
python zephyr-wolfmqtt-broker/tests/test_broker.py
```

Or with the Mosquitto clients:

```sh
mosquitto_sub -h 127.0.0.1 -t "greenhouse/#" -v
mosquitto_pub -h 127.0.0.1 -t "greenhouse/temp" -m "21.5" -q 1
```

## Run on a board

Use a 2.4 GHz Wi-Fi network that lets its devices talk to each other, such as a small router. Guest and university networks often block this.

```sh
cp zephyr-wolfmqtt-broker/wifi.local.conf.example zephyr-wolfmqtt-broker/wifi.local.conf
# put your network name and password in wifi.local.conf

west build -p always -b m5stack_fire/esp32/procpu -d build-fire zephyr-wolfmqtt-broker
west flash -d build-fire --esp-device /dev/ttyACM0
python -m serial.tools.miniterm /dev/ttyACM0 115200
```

The port can differ. Check it with `ls /dev/ttyACM* /dev/ttyUSB*`, before and after plugging in the board. For a XIAO ESP32-C6, use the board `xiao_esp32c6/esp32c6/hpcore`.

The board prints `board address: ...`. Test from a computer on the same network:

```sh
python zephyr-wolfmqtt-broker/tests/test_broker.py <board address>
```

## Memory

Limits are in `src/user_settings.h`. Current settings: 10 clients, 32 subscriptions, 8 retained messages of up to 256 bytes, MQTT 3.1.1 and 5.0, no TLS.

| Build | `MqttBroker` RAM | Image size |
|---|---|---|
| M5Stack Fire | 60,708 B | 585,728 B |
| XIAO ESP32-C6 | 60,708 B | 707,728 B |

The image size includes Zephyr, Wi-Fi and networking. With wolfMQTT's default sizes, the Fire build doesn't fit: RAM overflows by 119,672 bytes.

To see memory use at run time, build with the memory report:

```sh
west build -p always -b m5stack_fire/esp32/procpu -d build-mem zephyr-wolfmqtt-broker -- -DEXTRA_CONF_FILE=mem_report.conf
```

Every 10 seconds, the board prints the system heap use, which includes Wi-Fi, and the stack use of each thread.

## Licence

GPL-3.0-or-later, the same as wolfMQTT.
