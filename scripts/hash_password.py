import bcrypt, getpass
pw = getpass.getpass("Password: ").encode()
print(bcrypt.hashpw(pw, bcrypt.gensalt(12)).decode())