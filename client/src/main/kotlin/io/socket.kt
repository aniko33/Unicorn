package io

import java.net.*
import java.io.*

class SocketTCP(host: String, port: Int) {
    private var reader: InputStream
    private var writer: OutputStream
    var socketfd: Socket

    init {
        socketfd = Socket(host, port)
        writer = socketfd.getOutputStream()
        reader = socketfd.getInputStream()
    }

    fun send(data: ByteArray) {
        writer.write(data)
    }
    fun send(data: String) {
        writer.write(data.toByteArray())
    }

    fun recv(buffer: Int): ByteArray {
        val bufferArray = ByteArray(buffer)
        val result = ByteArrayOutputStream()
        var readed: Int;

        while (reader.read(bufferArray).also { readed = it } != -1 ){
            result.write(bufferArray, 0, readed)
        }

        return result.toByteArray()
    }

    fun recvString(buffer: Int): String {
        val result = StringBuilder()

        val bufferArray = recv(buffer)

        for (b in bufferArray) {
            result.append(b.toInt().toChar())
        }

        return result.toString()
    }
}