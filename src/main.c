/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include "broker_net.h"
#include "wifi.h"

static MqttBroker broker;
static MqttBrokerNet net;

int main(void)
{
	int rc;

	printk("MqttBroker uses %zu bytes of RAM\n", sizeof(broker));

#ifdef CONFIG_WIFI
	rc = wifi_connect();
	if (rc != 0) {
		return rc;
	}
#endif

	broker_net_init(&net);

	rc = MqttBroker_Init(&broker, &net);
	if (rc != MQTT_CODE_SUCCESS) {
		printk("init failed: %d\n", rc);
		return rc;
	}

	rc = MqttBroker_Run(&broker);
	printk("broker stopped: %d\n", rc);
	return rc;
}
