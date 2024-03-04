#include <cJSON.h>
#include <string.h>
#include <sys/socket.h>

#ifndef COMMANDS_H
#define COMMANDS_H

void cmd_ping(int client_fd, int job) {
  cJSON *response = cJSON_CreateObject();
  cJSON_AddStringToObject(response, "output", "pong");
  cJSON_AddBoolToObject(response, "success", 1);
  cJSON_AddNumberToObject(response, "job", job);
  cJSON_AddStringToObject(response, "type", "cmdout");

  char *response_str = cJSON_Print(response);

  send(client_fd, response_str, strlen(response_str), 0);

  cJSON_free(response);
}

#endif
