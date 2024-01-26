use std::net::TcpStream;
use std::io::{self, Write, Read};

use salsa20::cipher::{StreamCipher, StreamCipherSeek};
use salsa20::{cipher::KeyIvInit, Salsa20};

pub struct EncryptedTunnel {
    _key: Vec<u8>,
    _iv: Vec<u8>,
    pub socket: TcpStream,
}

impl EncryptedTunnel {
    pub fn new(key: &[u8], iv: &[u8], socket: TcpStream) -> Self {

        Self {
            _key: key.to_vec(),
            _iv: iv.to_vec(),
            socket,
        }
    }

    pub fn send(&mut self, data: &[u8]) -> Result<(), io::Error> {
        let mut output: Vec<u8> = Vec::from(data);

        let mut cipher = Salsa20::new(self._key.as_slice().into(), self._iv.as_slice().into());
        cipher.apply_keystream(&mut output);

        self.socket.write_all(&output)?;

        Ok(())
    }

    pub fn sendvec(&mut self, mut data: Vec<u8>) -> Result<(), io::Error> {
        let mut cipher = Salsa20::new(self._key.as_slice().into(), self._iv.as_slice().into());
        cipher.apply_keystream(data.as_mut_slice());

        self.socket.write_all(&data)?;

        Ok(())
    }

    pub fn recv(&mut self, buffer: &mut [u8]) -> Result<Vec<u8>, io::Error> {
        let mut cipher = Salsa20::new(self._key.as_slice().into(), self._iv.as_slice().into());

        let readed = self.socket.read(buffer)?;
        let getted = &mut buffer[..readed];

        cipher.seek(0u32);
        cipher.apply_keystream(getted);

        Ok(getted.to_vec())
    }
}


