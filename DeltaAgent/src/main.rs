use std::io::{self, Read, Write};
use std::net::TcpStream;
use typenum::consts::U10;
use salsa20::SalsaCore;
use salsa20::cipher::{StreamCipherCoreWrapper, StreamCipher, StreamCipherSeek};
use salsa20::{Salsa20, cipher::KeyIvInit};
use flate2::{write::ZlibEncoder, Compression};
use rand::{distributions::Alphanumeric, Rng};
use rsa::pkcs1::DecodeRsaPublicKey;
use rsa::{Pkcs1v15Encrypt, RsaPublicKey};

// TODO: add commands

const BUFFER: usize = 1024;
struct EncryptedTunnel {
    _key: Vec<u8>,
    _iv: Vec<u8>,
    cipher: StreamCipherCoreWrapper<SalsaCore<U10>>,
    socket: TcpStream,
}

impl EncryptedTunnel {
    fn new(key: &[u8], iv: &[u8], socket: TcpStream) -> Self {
        let cipher = Salsa20::new(key.into(), iv.into());
        
        Self {
            _key: key.to_vec(),
            _iv: iv.to_vec(),
            socket,
            cipher
        }
    }

    fn send(&mut self, mut data: Vec<u8>) -> Result<(), io::Error> {
        self.cipher.apply_keystream(data.as_mut_slice());

        self.socket.write_all(&data)?;

        Ok(())
    }

    fn recv(&mut self, buffer: &mut [u8]) -> Result<Vec<u8>, io::Error> {
        let readed = self.socket.read(buffer)?;
        let getted = &mut buffer[..readed];

        self.cipher.seek(0u32);
        self.cipher.apply_keystream(getted);

        Ok(getted.to_vec())
    }
}

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

    let mut socket = TcpStream::connect("127.0.0.1:8888")?;

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
        let key_iv_compressed = Vec::new();
        let mut keyiv_concat: Vec<u8> = Vec::new();

        keyiv_concat.extend(&key);
        keyiv_concat.extend_from_slice(b"<SPR>");
        keyiv_concat.extend(&iv);

        let mut encoder = ZlibEncoder::new(key_iv_compressed, Compression::new(8));
        encoder.write_all(&keyiv_concat[..]).unwrap();

        socket.write_all(
            &public_key
                .encrypt(&mut rng, Pkcs1v15Encrypt, &encoder.finish().unwrap()[..])
                .unwrap(),
        )?;
    }

    let mut enctunnel = EncryptedTunnel::new(key.as_slice(), iv.as_slice(), socket);

    loop {
        let cmd = String::from_utf8(enctunnel.recv(&mut buffer)?).unwrap();

        match cmd.as_str() {
            "2" => enctunnel.send(b"3".to_vec())?,
            _ => ()
        }

    }
}
