/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/sys_heap.h>
#include <zephyr/debug/thread_analyzer.h>

/* Wi-Fi allocates from the system heap */
extern struct k_heap _system_heap;

static void mem_report(void)
{
	struct sys_memory_stats s;

	while (1) {
		k_sleep(K_SECONDS(10));
		sys_heap_runtime_stats_get(&_system_heap.heap, &s);
		printk("heap: used %zu, peak %zu, free %zu\n",
		       s.allocated_bytes, s.max_allocated_bytes, s.free_bytes);
		thread_analyzer_print(0);
	}
}

K_THREAD_DEFINE(mem_report_id, 2048, mem_report, NULL, NULL, NULL, 14, 0, 0);
