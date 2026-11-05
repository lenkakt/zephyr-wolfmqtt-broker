/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/net/net_if.h>
#include <zephyr/net/net_ip.h>
#include <zephyr/net/net_mgmt.h>
#include <zephyr/net/wifi_mgmt.h>
#include <zephyr/sys/printk.h>

#include "wifi.h"

#define ADDR_WAIT_SEC 30

static int wifi_request(struct net_if *iface)
{
	struct wifi_connect_req_params params = {
		.ssid = (const uint8_t *)CONFIG_APP_WIFI_SSID,
		.ssid_length = strlen(CONFIG_APP_WIFI_SSID),
		.psk = (const uint8_t *)CONFIG_APP_WIFI_PSK,
		.psk_length = strlen(CONFIG_APP_WIFI_PSK),
		.security = strlen(CONFIG_APP_WIFI_PSK) > 0 ? WIFI_SECURITY_TYPE_PSK
							    : WIFI_SECURITY_TYPE_NONE,
		.channel = WIFI_CHANNEL_ANY,
		.band = WIFI_FREQ_BAND_2_4_GHZ,
		.timeout = SYS_FOREVER_MS,
	};

	return net_mgmt(NET_REQUEST_WIFI_CONNECT, iface, &params, sizeof(params));
}

int wifi_connect(void)
{
	struct net_if *iface = net_if_get_wifi_sta();
	char ip[NET_IPV4_ADDR_LEN];

	if (iface == NULL) {
		printk("no Wi-Fi interface\n");
		return -ENODEV;
	}
	if (strlen(CONFIG_APP_WIFI_SSID) == 0) {
		printk("no Wi-Fi name, see wifi.local.conf.example\n");
		return -EINVAL;
	}

	while (true) {
		printk("connecting to Wi-Fi network %s\n", CONFIG_APP_WIFI_SSID);

		int rc = wifi_request(iface);

		if (rc != 0) {
			printk("Wi-Fi request failed: %d\n", rc);
		}

		for (int i = 0; i < ADDR_WAIT_SEC; i++) {
			struct net_in_addr *addr =
				net_if_ipv4_get_global_addr(iface, NET_ADDR_PREFERRED);

			if (addr != NULL) {
				net_addr_ntop(NET_AF_INET, addr, ip, sizeof(ip));
				printk("board address: %s\n", ip);
				return 0;
			}
			k_sleep(K_SECONDS(1));
		}
		printk("no address yet, trying again\n");
	}
}
