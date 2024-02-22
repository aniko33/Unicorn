import pip, sys

try:
    from OpenSSL import crypto
except ModuleNotFoundError:
    if hasattr(pip, 'main'):
        pip.main(['install', "pyopenssl"])
    else:
        pip._internal.main(['install', "pyopenssl"])

# https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python

if len(sys.argv) < 2:
    print("Usage: {} <output_dir>".format(sys.argv[0]))
    quit(1)

output_dir = sys.argv[1]

emailAddress="dontexist@email.com"
commonName="Unicorn"
countryName="NT"
localityName="Ohio"
stateOrProvinceName="US"
organizationName="Unicorn corp."
organizationUnitName="Unicorn corp."
serialNumber=0
validityStartInSeconds=0
validityEndInSeconds=10*365*24*60*60
KEY_FILE  = output_dir + "/domain.key"
CERT_FILE = output_dir + "/domain.crt"

#can look at generated file using openssl:
#openssl x509 -inform pem -in selfsigned.crt -noout -text
# create a key pair
k = crypto.PKey()
k.generate_key(crypto.TYPE_RSA, 4096)
# create a self-signed cert

cert = crypto.X509()
cert.get_subject().C = countryName
cert.get_subject().ST = stateOrProvinceName
cert.get_subject().L = localityName
cert.get_subject().O = organizationName
cert.get_subject().OU = organizationUnitName
cert.get_subject().CN = commonName
cert.get_subject().emailAddress = emailAddress
cert.set_serial_number(serialNumber)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(validityEndInSeconds)
cert.set_issuer(cert.get_subject())
cert.set_pubkey(k)
cert.sign(k, 'sha512')
with open(CERT_FILE, "wt") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
with open(KEY_FILE, "wt") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
