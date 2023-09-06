use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Key, Nonce,
};
use rand::{distributions::Alphanumeric, Rng};
use rsa::{pkcs1::DecodeRsaPublicKey, Pkcs1v15Encrypt, RsaPublicKey};
use std::net::TcpStream;
use tungstenite::{connect, stream::MaybeTlsStream, Message, WebSocket};

struct EncryptedTunnel {
    key: Vec<u8>,
    nonce: Vec<u8>,
    cipher: Aes256Gcm,
    socket: WebSocket<MaybeTlsStream<TcpStream>>,
}
impl EncryptedTunnel {
    fn new(key: Vec<u8>, nonce: Vec<u8>, socket: WebSocket<MaybeTlsStream<TcpStream>>) -> Self {
        Self {
            cipher: Aes256Gcm::new(&Key::<Aes256Gcm>::from_slice(&key)),
            key,
            nonce,
            socket,
        }
    }

    fn send(&mut self, c: Vec<u8>) -> Option<()> {
        match self.socket.send(Message::Binary(
            self.cipher
                .encrypt(Nonce::from_slice(self.nonce.as_slice()), c.as_slice())
                .unwrap(),
        )) {
            Ok(_) => Some(()),
            Err(_) => None,
        }
    }
    fn recv(&mut self) -> Vec<u8> {
        Message::binary(self.socket.read().unwrap()).into_data()
    }
}

fn random_bytes(l: usize) -> Vec<u8> {
    let rand: String = rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(l)
        .map(char::from)
        .collect();
    rand.as_bytes().to_vec()
}

fn connection(mut etunnel: EncryptedTunnel) {
    loop {
        let msg = String::from_utf8(etunnel.recv()).unwrap();

        match msg {
            _ => {}
        }
    }
}

fn main() {
    let key = random_bytes(32);
    let nonce = random_bytes(16);

    let mut rng = rand::thread_rng();

    let (mut client, _) =
        connect(url::Url::parse("ws://127.0.0.1:8080/websocket").unwrap()).unwrap();

    client.send(Message::text("Unicorn".to_string())).unwrap();
    let rsa_public =
        RsaPublicKey::from_pkcs1_pem(client.read().unwrap().to_string().as_str()).unwrap();

    let mut etunnel = EncryptedTunnel::new(key, nonce, client);

    etunnel
        .socket
        .send(Message::Binary(
            rsa_public
                .encrypt(
                    &mut rng,
                    Pkcs1v15Encrypt,
                    format!(
                        "{}&{}",
                        String::from_utf8(etunnel.key.clone()).unwrap(),
                        String::from_utf8(etunnel.nonce.clone()).unwrap()
                    )
                    .as_bytes(),
                )
                .unwrap(),
        ))
        .unwrap();

    connection(etunnel);
}
