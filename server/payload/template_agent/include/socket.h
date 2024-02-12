#include <stdio.h>
#include <stdbool.h>
#include <cJSON.h>

#ifndef SOCKET_H
#define SOCKET_H

int connect_server_c2(char* addr, int port);
ssize_t bsend(int fd, char* buffer, int buffer_size);
ssize_t brecv(int fd, char* buffer, int n);
ssize_t rrecv(int fd, char* buffer, int n);
ssize_t send_str(int fd, char* __str);
cJSON* recv_json(int client_fd, int n_byte); 
char* frecv(int fd, int buffer_size);
size_t send_response(int client_fd, char* output, bool success, int job);


#endif


