package io

import java.util.Base64
import java.security.PrivateKey
import java.security.PublicKey
import java.security.KeyPairGenerator

import org.bouncycastle.crypto.engines.Salsa20Engine
import org.bouncycastle.crypto.params.KeyParameter
import org.bouncycastle.crypto.params.ParametersWithIV
import org.bouncycastle.asn1.pkcs.PrivateKeyInfo
import org.bouncycastle.asn1.x509.SubjectPublicKeyInfo
import org.bouncycastle.util.io.pem.PemObject
import org.bouncycastle.util.io.pem.PemWriter

import java.io.StringWriter

import java.security.KeyPair
import javax.crypto.Cipher

interface CryptoInterface {
    fun encrypt(data: ByteArray): ByteArray
    fun encrypt(data: String): ByteArray
    fun encryptBase64(data: ByteArray): String
    fun encryptBase64(data: String): String
    fun decrypt(data: ByteArray): ByteArray
}

class Salsa20(EncryptionKey: ByteArray, IV: ByteArray) : CryptoInterface {
    var key: ByteArray
    var iv: ByteArray
    init {
        key = EncryptionKey
        iv = IV
    }

    override fun encrypt(data: ByteArray): ByteArray {
        val cipher = Salsa20Engine()
        cipher.init(true, ParametersWithIV(KeyParameter(key), iv))

        val encrypted = ByteArray(data.size)
        cipher.processBytes(data, 0, data.size, encrypted, 0)

        return encrypted
    }

    override fun encrypt(data: String): ByteArray {
        val encrypted = encrypt(data.toByteArray())

        return encrypted
    }

    override fun encryptBase64(data: ByteArray): String {
        val encrypted = encrypt(data)

        return Base64.getEncoder().encode(encrypted).toString()
    }

    override fun encryptBase64(data: String): String {
        val encrypted = encrypt(data.toByteArray())

        return Base64.getEncoder().encode(encrypted).toString()
    }

    override fun decrypt(data: ByteArray): ByteArray {
        val cipher = Salsa20Engine()
        cipher.init(false, ParametersWithIV(KeyParameter(key), iv))

        val decrypted = ByteArray(data.size)

        cipher.processBytes(data, 0, data.size, decrypted, 0)

        return decrypted
    }

    fun decrypt_UTF(data: ByteArray): String {
        val decrypted = decrypt(data)

        return String(decrypted, Charsets.UTF_8)
    }
}

class RSA(priv_key: PrivateKey, pub_key: PublicKey) : CryptoInterface {
    var encryption_cipher: Cipher
    var decryption_cipher: Cipher

    var public_key: PublicKey
    var private_key: PrivateKey

    init {
        encryption_cipher = Cipher.getInstance("RSA")
        decryption_cipher = Cipher.getInstance("RSA")

        encryption_cipher.init(Cipher.ENCRYPT_MODE, pub_key)
        decryption_cipher.init(Cipher.DECRYPT_MODE, priv_key)

        private_key = priv_key
        public_key = pub_key
    }

    override fun encrypt(data: ByteArray): ByteArray {
        return encryption_cipher.doFinal(data)
    }

    override fun encrypt(data: String): ByteArray {
        return encrypt(data.toByteArray())
    }

    override fun encryptBase64(data: ByteArray): String {
        val encrypted = encrypt(data)

        return Base64.getEncoder().encode(encrypted).toString()
    }

    override fun encryptBase64(data: String): String {
        val encrypted = encrypt(data.toByteArray())

        return Base64.getEncoder().encodeToString(encrypted)
    }

    override fun decrypt(data: ByteArray): ByteArray {
        return decryption_cipher.doFinal(data)
    }

    fun decrypt_UTF(data: ByteArray): String {
        val decrypted = decrypt(data)
        return String(decrypted, Charsets.UTF_8)
    }

    fun export_private(): String {
        val string_pem = StringWriter()

        val private_encoded = private_key.encoded
        val pkinfo = PrivateKeyInfo.getInstance(private_encoded)
        val private_key_pkcs1 = pkinfo.parsePrivateKey().toASN1Primitive().getEncoded()

        val pemObj = PemObject("RSA PRIVATE KEY", private_key_pkcs1)
        val pemW = PemWriter(string_pem)
        pemW.writeObject(pemObj)
        pemW.close()

        return string_pem.toString()
    }
    fun export_public(): String {
        val string_pem = StringWriter()

        val public_encoded = public_key.encoded
        val spkinfo = SubjectPublicKeyInfo.getInstance(public_encoded)
        val public_key_pkcs1 = spkinfo.parsePublicKey().getEncoded()

        val pemObj = PemObject("RSA PUBLIC KEY", public_key_pkcs1)
        val pemW = PemWriter(string_pem)
        pemW.writeObject(pemObj)
        pemW.close()

        return string_pem.toString()
    }

    companion object {
        fun generate_keys(size: Int): KeyPair {
            val key_generator = KeyPairGenerator.getInstance("RSA")
            key_generator.initialize(size)
            return key_generator.generateKeyPair()
        }
    }
}

class EncryptedTunnel(sConn: SocketTCP, encryptionSalsa: Salsa20) {
    var socket: SocketTCP
    var encryption: Salsa20

    init {
        socket = sConn
        encryption = encryptionSalsa
    }

    fun send(data: ByteArray) {
        socket.send(encryption.encrypt(data))
    }

    fun send(data: String) {
        socket.send(encryption.encrypt(data))
    }

    fun recv(size: Int): ByteArray {
        return encryption.decrypt(socket.recv(size))
    }

    fun recvUTF(size: Int): String {
        return encryption.decrypt_UTF(socket.recv(size))
    }
}