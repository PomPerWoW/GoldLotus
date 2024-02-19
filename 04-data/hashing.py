
import hashlib

hash_algorithm = hashlib.new("SHA256")

def hashPassword(password):
    hash_algorithm.update(password.encode())
    return hash_algorithm.hexdigest()
