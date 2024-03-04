#include <stdio.h>
#include <stdbool.h>
#include <cJSON.h>
#include <sys/types.h>

#ifndef SOCKET_H
#define SOCKET_H

int connect_server_c2(char* addr, int port);
int sendall(int socket_fd, const char *buffer, size_t length, int flags);
char* frecv(int fd, int buffer_size);


#endif


