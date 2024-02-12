#include <string.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <stdbool.h>
#include <stdio.h>
#include <cJSON.h>

int connect_server_c2(char* addr, int port) {
  struct sockaddr_in server_in;
  int client_fd;
  
  server_in.sin_family = AF_INET;
  server_in.sin_addr.s_addr = inet_addr(addr);
  server_in.sin_port = htons(port);

  if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    perror("Socker creation failed");
    return -1;
  } 

  if (connect(client_fd, (struct sockaddr*) &server_in, sizeof(server_in)) < 0) {
    perror("Connection failed");
    return -1;
  }

  return client_fd;
}

long bsend(int fd, char* buffer, int buffer_size) {
  return send(fd, buffer, buffer_size, 0);
}

long brecv(int fd, char* buffer, int n) {
  return recv(fd, buffer, n, 0);
}

long rrecv(int fd, char* buffer, int n) {
  long n_bytes = recv(fd, buffer, n, 0);
  
  buffer[n_bytes] = '\0';
  
  return n_bytes;
}

long send_str(int fd, char* __str) {
  return send(fd, __str, strlen(__str), 0);
}

char* frecv(int fd, int buffer_size) {
  char* buffer = (char*) malloc(buffer_size);
  int readed = recv(fd, buffer, buffer_size, 0);

  buffer = (char*) realloc(buffer, readed);
  
  buffer[readed] = '\0';

  return buffer;
}

long send_response(int client_fd, char* output, bool success, int job) {
  cJSON *json = cJSON_CreateObject();
  cJSON_AddBoolToObject(json, "success", true);
  cJSON_AddStringToObject(json, "output", output);
  cJSON_AddNumberToObject(json, "job", job);

  char* json_str = cJSON_Print(json);

  long status = send_str(client_fd, json_str);

  cJSON_free(json_str);
  cJSON_Delete(json);

  return status;
}

cJSON* recv_json(int client_fd, int n_byte) {
  char* buffer = frecv(client_fd, n_byte);

  cJSON *json = cJSON_Parse(buffer);

  free(buffer);

  if (json == NULL) {
    cJSON_Delete(json);
    return NULL;
  }

  return json;
}
