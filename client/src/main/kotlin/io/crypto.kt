package io

import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

/*
    TODO -> add AES encryption Python compatible
*/

class AES(key: ByteArray, iv: ByteArray) {
    private var encryption_cipher: Cipher
    private var decryption_cipher: Cipher
    init {
        encryption_cipher = Cipher.getInstance("AES/CBC/NoPadding")
        decryption_cipher = Cipher.getInstance("AES/CBC/NoPadding")


        encryption_cipher.init(Cipher.ENCRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(iv))
        decryption_cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(iv))
    }

    fun encrypt(data: ByteArray): ByteArray {
        return encryption_cipher.doFinal(data)
    }

    fun decrypt(data: ByteArray): ByteArray {
        return decryption_cipher.doFinal(data)
    }
}