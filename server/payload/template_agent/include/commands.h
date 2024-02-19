#include "socket.h"
#include <cJSON.h>

#ifndef COMMANDS_H
#define COMMANDS_H

void confirm(int fd) { // [ Create a confirm for handshake ]
  {
    char buf[3];
    brecv(fd, buf, 2);
  }
}

void cmd_ping(int client_fd, int job) {
  cJSON *response = cJSON_CreateObject();
  cJSON_AddStringToObject(response, "output", "pong");
  cJSON_AddBoolToObject(response, "success", 1);
  cJSON_AddNumberToObject(response, "job", job);
  cJSON_AddStringToObject(response, "type", "cmdout");

  send_str(client_fd, cJSON_Print(response));

  cJSON_free(response);
}

// TODO ...

void test_download(int client_fd, int job) {
  cJSON *response = cJSON_CreateObject();
  cJSON_AddStringToObject(response, "filename", "sesso.png");
  cJSON_AddBoolToObject(response, "success", 1);
  cJSON_AddNumberToObject(response, "job", job);
  cJSON_AddStringToObject(response, "type", "download");

  send_str(client_fd, cJSON_Print(response));

  cJSON_Delete(response);

  confirm(client_fd);

  sendall(client_fd, "ciao", strlen("ciao"), 0);

}

#endif
