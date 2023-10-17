#include <iostream>
#include <string>

#include <arpa/inet.h> 
#include <stdio.h> 
#include <string.h> 
#include <sys/socket.h> 
#include <unistd.h> 

#include <cryptopp/salsa.h>
#include <cryptopp/rsa.h>

using namespace std;
using namespace CryptoPP;

#define SERVER_ADDR "127.0.0.1"
#define SERVER_PORT 6666

struct EncryptedTunnel {
    Salsa20::Encryption cipher_encrypt;
    Salsa20::Decryption cipher_decrypt;
};

void make_new() {}

int main(int argc, char* argv[]) {    
    char buffer[1024] = { 0 };
    
    int socketfd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in socketconn;

    socketconn.sin_family = AF_INET;
    socketconn.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_ADDR, &socketconn.sin_addr);

    connect(socketfd, (struct sockaddr*)&socketconn, sizeof(socketconn));

    send(socketfd, "ciao", 4, 0);

    return 0;
}