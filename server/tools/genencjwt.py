import rsa, sys

if len(sys.argv) < 3:
    print("Usage: {} <size> <output_dir>".format(sys.argv[0]))
    quit(1)

size = int(sys.argv[1])
output_dir = sys.argv[2]

_, privkey = rsa.newkeys(size)

with open(output_dir + "/jwt.key", "wb") as f:
    f.write(rsa.PrivateKey.save_pkcs1(privkey))
