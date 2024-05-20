#define _SVID_SOURCE
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>

#include "../../../include/button.h"
#include "../../../include/led.h"
#include "../../../include/uart.h"

#include "../../../include/myconfig.h"

#define SLEEP_TIME_MS 1000

/* size of stack area used by each thread */
#define STACKSIZE 1024

/* scheduling priority used by each thread */
#define LED_PRIORITY 6
#define UART_PRIORITY 7
#define MAIN_PRIORITY 5

/*
0: Green
1: Blue
2: Red
*/
int led = 2;

int led_time = 0;

void led_thread(void) {
  while (1) {
    if (led == 0) {
      set_led_blue(0);
      set_led_red(0);
      toggle_led_green();
    } else if (led == 1) {
      set_led_green(0);
      set_led_red(0);
      toggle_led_blue();
    } else if (led == 2) {
      set_led_green(0);
      set_led_blue(0);
      toggle_led_red();
    }

    k_msleep(SLEEP_TIME_MS);
    led_time += 1;
  }
}

int last_switch_time = 0;

void main_thread(void) {
  while (1) {
    uint8_t msg[BUF_SIZE] = {0};
    int ret;

    // Receive a message from the queue
    ret = k_msgq_get(&uart_queue, msg, K_FOREVER);
    if (ret != 0) {
      printk("Failed to receive message from queue\n");
      continue;
    }

    if ((led_time - last_switch_time) < 5) {
      continue;
    }

    led += 1;
    if (led > 2) {
      led = 0;
    }

    last_switch_time = led_time;
  }
}

int main(void) {
  // Init functions
  led_init();

  return 0;
}

// Starting threads
K_THREAD_DEFINE(led_thread_id, STACKSIZE, led_thread, NULL, NULL, NULL,
                LED_PRIORITY, 0, 0);

K_THREAD_DEFINE(uart_thread_id, STACKSIZE, uart_thread, NULL, NULL, NULL,
                UART_PRIORITY, 0, 0);

K_THREAD_DEFINE(main_thread_id, STACKSIZE, main_thread, NULL, NULL, NULL,
                MAIN_PRIORITY, 0, 0);