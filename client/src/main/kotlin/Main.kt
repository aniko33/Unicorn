import io.*

const val BUFFER_SIZE = 1024
const val HOST = "127.0.0.1"
const val PORT = 6666

fun main() {
    val username = "aniko"

    val keys = RSA.generate_keys(1024)
    val rsa = RSA(keys.private, keys.public)

    val client = SocketTCP(HOST, PORT)

    val fingerprint = client.recv(BUFFER_SIZE)
    client.send(rsa.export_public())

    val salsa20Keys = rsa.decrypt(client.recv(BUFFER_SIZE))

    val sKey = salsa20Keys.copyOfRange(0, 32)
    val sIV  = salsa20Keys.copyOfRange(32, 32+8)

    var encTunnel = EncryptedTunnel(client, Salsa20(sKey, sIV))

    encTunnel.send(username)

    val victims = encTunnel.recvUTF(BUFFER_SIZE).split("\n")

    for ((i, victim) in victims.withIndex()) {
        println("$i: $victim")
    }

    encTunnel = EncryptedTunnel(client, Salsa20(sKey, sIV))

    val chooice = readLine()
    encTunnel.send(victims[chooice!!.toInt()])


}