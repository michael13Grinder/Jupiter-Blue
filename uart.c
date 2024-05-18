#include "../include/uart.h"

K_MSGQ_DEFINE(uart_queue, sizeof(uint8_t[BUF_SIZE]), QUEUE_SIZE, 4);

// Function to send a string over UART
void send_str(const struct device *uart, char *str) {
  if (!device_is_ready(usart_dev)) {
    printk("USART device not found!");
    return;
  }

  int msg_len = strlen(str);

  for (int i = 0; i < msg_len; i++) {
    uart_poll_out(uart, str[i]);
  }

  printk("Device %s sent: \"%s\"\n", uart->name, str);
}

// Function to receive a string from UART
void recv_str(const struct device *uart, char *str) {
  if (!device_is_ready(usart_dev)) {
    printk("USART device not found!");
    return;
  }

  char *head = str;
  char c;

  while (!uart_poll_in(uart, &c)) {
    *head++ = c;
  }
  *head = '\0';
}

// Thread function to handle UART communication
void uart_thread() {
  while (1) {
    char recv_buf[BUF_SIZE] = {0};
    char send_buf[BUF_SIZE] = {0};
    int count = 0;
    while (1) {
      recv_str(usart_dev, recv_buf);

      if (recv_buf[0] == 0x0E) {
        continue;
      }

      // If final byte is 0xFF, then the message breaks
      if (recv_buf[0] == 0xFF) {
        send_buf[count] = '\0';
        break;
      }

      if (recv_buf[0] != 0) {
        send_buf[count] = recv_buf[0];
        count += 1;
      }

      k_sleep(K_MSEC(5));
    }
    // Add message to the message queue
    int ret = k_msgq_put(&uart_queue, send_buf, K_NO_WAIT);
    if (ret != 0) {
      // printk("Failed to add message to queue\n");
    }
  }
}