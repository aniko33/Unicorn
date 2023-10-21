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
        writer.flush()
    }
    fun send(data: String) {
        send(data.toByteArray())
    }

    fun recv(buffer: Int): ByteArray {
        val bufferArray = ByteArray(buffer)

        val byteRead = reader.read(bufferArray)
        val result = ByteArray(byteRead)

        for (i in 0..<byteRead) {
            result[i] = bufferArray[i]
        }

        return result
    }
    fun recvString(buffer: Int): String {
        val bufferArray = recv(buffer)

        return bytesToString(bufferArray)
    }

    companion object {
        fun bytesToString(data: ByteArray): String {
            val rString = StringBuilder()

            for (b in data) {
                rString.append(b.toInt().toChar())
            }

            return rString.toString()
        }
    }
}