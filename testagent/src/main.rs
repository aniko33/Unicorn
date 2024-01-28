mod commands;
mod crypto;
mod response;

use crate::crypto::EncryptedTunnel;
use crate::response::CmdReceived;

use std::collections::HashMap;
use std::io::{self, Read, Write};
use std::net::TcpStream;

use rand::{distributions::Alphanumeric, Rng};
use rsa::pkcs1::DecodeRsaPublicKey;
use rsa::{Pkcs1v15Encrypt, RsaPublicKey};

type CommandFunction = Box<dyn Fn(&mut EncryptedTunnel, i64)>;

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

fn init_connection(
    mut conn: TcpStream,
    mut buffer: [u8; BUFFER],
) -> Result<EncryptedTunnel, io::Error> {
    let fingerprint: String = generate_fingerprint();

    let mut rng = rand::thread_rng();

    conn.write_all(fingerprint.as_bytes())?;

    let public_key = {
        let readed = conn.read(&mut buffer)?;
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

        conn.write_all(
            &public_key
                .encrypt(&mut rng, Pkcs1v15Encrypt, &keyiv_concat)
                .unwrap(),
        )?;
    }

    let enctunnel = EncryptedTunnel::new(key.as_slice(), iv.as_slice(), conn);

    return Ok(enctunnel);
}

fn main() -> Result<(), io::Error> {
    let mut buffer: [u8; 1024] = [0; BUFFER];

    let socket = TcpStream::connect("127.0.0.1:7777")?;

    let mut enctunnel = init_connection(socket, buffer).expect("Init connection failed");

    let mut commands: HashMap<&str, CommandFunction> = HashMap::new();
    commands.insert("ping", Box::new(commands::ping));

    loop {
        let cmd = String::from_utf8(enctunnel.recv(&mut buffer)?).unwrap();
        let cmd = cmd.as_str();

        println!("{}", cmd);

        match serde_json::from_str::<CmdReceived>(cmd) {
            Ok(cmd_json) => {
                let cmd_exec = cmd_json.exec.as_str();

                if commands.contains_key(&cmd_exec) {
                    match commands.get(cmd_exec) {
                        Some(cmd_func) => cmd_func(&mut enctunnel, cmd_json.job),
                        None => (),
                    }
                }
            }
            Err(_) => {
                enctunnel.socket.write_all(b"3").unwrap();
            }
        }
    }
}
