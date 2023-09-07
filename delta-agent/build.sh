random_str=$(openssl rand -base64 125)

export LITCRYPT_ENCRYPT_KEY=$random_str
cargo build --target x86_64-pc-windows-gnu
