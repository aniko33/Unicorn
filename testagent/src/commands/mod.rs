use crate::crypto::EncryptedTunnel;

pub fn ping(connection: &mut EncryptedTunnel) {
    connection.send(b"test").unwrap();
}
