use serde::{Serialize, Deserialize};

#[derive(Serialize)]
struct JobResponse {
    output: String,
    success: bool,
    job: i64
}

#[derive(Deserialize)]
pub struct CmdReceived {
    pub job: i64,
    pub exec: String,
}

pub fn job_response(output: String, success: bool, job: i64) -> String {
    return serde_json::to_string(&JobResponse {output, success, job} ).unwrap();
}
