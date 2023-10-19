package io

import java.net.*
import java.io.*

class SocketTCP(host: String, port: Int) {
    private var iStream: DataInputStream
    private var oStream: DataOutputStream
    var socketfd: Socket

    init {
        socketfd = Socket(host, port)
        iStream = DataInputStream(socketfd.getInputStream())
        oStream = DataOutputStream(socketfd.getOutputStream())
    }

    fun send(data: ByteArray) {
        oStream.write(data)
    }

    fun recv(buffer: Int): ByteArray {
        val bufferArray = ByteArray(buffer)
        iStream.readFully(bufferArray)

        return bufferArray
    }

    fun recvString(buffer: Int): String {
        val bufferArray = ByteArray(buffer)
        val result = StringBuilder()

        iStream.readFully(bufferArray)

        for (b in bufferArray) {
            result.append(b.toInt().toChar())
        }

        return result.toString()
    }

    fun recvUTF(buffer: Int): String {
        val bufferArray = ByteArray(buffer)
        val result = iStream.readUTF()

        return result
    }
}