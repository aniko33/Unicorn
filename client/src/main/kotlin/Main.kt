import io.*

const val BUFSIZE = 1024
const val HOST = "127.0.0.1"
const val PORT = 6666

// TODO: Fix recv -> sockets

fun main() {
    val client = SocketTCP(HOST, PORT)
    val keys = RSA.generate_keys(1024)
    val rsa = RSA(keys.private, keys.public)

    client.send("ciao")
    val r = client.recv(BUFSIZE)

    println(r)
}