# SPDX-License-Identifier: GPL-3.0-or-later
cmake_minimum_required(VERSION 3.20.0)

# A manual copy, for workspaces where west doesn't provide wolfMQTT
if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/deps/wolfmqtt)
  list(APPEND ZEPHYR_EXTRA_MODULES ${CMAKE_CURRENT_LIST_DIR}/deps/wolfmqtt)
endif()

if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/wifi.local.conf AND NOT BOARD MATCHES "^native_sim")
  list(APPEND EXTRA_CONF_FILE ${CMAKE_CURRENT_LIST_DIR}/wifi.local.conf)
endif()

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(wolfmqtt_broker)

target_sources(app PRIVATE src/main.c src/broker_net.c)
target_sources_ifdef(CONFIG_WIFI app PRIVATE src/wifi.c)
target_sources_ifdef(CONFIG_APP_MEM_REPORT app PRIVATE src/mem_report.c)
target_include_directories(app PRIVATE src)
zephyr_compile_definitions(WOLFMQTT_USER_SETTINGS)
