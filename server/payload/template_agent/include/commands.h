#include "socket.h"

#ifndef COMMANDS_H
#define COMMANDS_H

void cmd_ping(int client_fd, int job) {
  send_response(client_fd, "pong", true, job);
}

#endif
