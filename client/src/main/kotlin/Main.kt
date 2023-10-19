import io.*

fun main() {
    val s = SocketTCP("127.0.0.1", 8888)
    val result = s.recvString(1024)

    println(result)
}
