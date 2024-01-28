use crate::crypto::EncryptedTunnel;
use crate::response::job_response;

pub fn ping(connection: &mut EncryptedTunnel, job: i64) {
    println!("{}", job);
    connection.send(job_response("test".to_string(), true, job).as_bytes()).unwrap();
}
