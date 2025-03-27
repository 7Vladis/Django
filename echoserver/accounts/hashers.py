from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
import bcrypt
import base64


class BCryptPasswordHasher(BasePasswordHasher):
    algorithm = "bcrypt_custom"
    log_rounds = 12

    def encode(self, password, salt, iterations=None):
        assert password is not None

        if iterations is None:
            iterations = self.log_rounds

        password_bytes = password.encode('utf-8')

        salt_bytes = bcrypt.gensalt(rounds=iterations)

        hash_value = bcrypt.hashpw(password_bytes, salt_bytes)

        salt_str = salt_bytes.decode('utf-8').split('$')[3][:22]
        hash_str = hash_value.decode('utf-8').split('$')[3][22:]

        salt_b64 = base64.b64encode(salt_str.encode('utf-8')).decode('utf-8')
        hash_b64 = base64.b64encode(hash_str.encode('utf-8')).decode('utf-8')

        encoded = f"{self.algorithm}${iterations}${salt_b64}${hash_b64}"
        return encoded

    def verify(self, password, encoded):
        algorithm, log_rounds, salt_b64, hash_b64 = encoded.split('$', 3)
        assert algorithm == self.algorithm

        salt_str = base64.b64decode(salt_b64).decode('utf-8')
        hash_str = base64.b64decode(hash_b64).decode('utf-8')

        salt_bytes = f"$2b${log_rounds}${salt_str}".encode('utf-8')

        password_bytes = password.encode('utf-8')
        expected_hash = bcrypt.hashpw(password_bytes, salt_bytes)

        expected_hash_str = expected_hash.decode('utf-8').split('$')[3][22:]
        expected_hash_b64 = base64.b64encode(expected_hash_str.encode('utf-8')).decode('utf-8')

        return constant_time_compare(hash_b64, expected_hash_b64)

    def safe_summary(self, encoded):
        algorithm, log_rounds, salt_b64, hash_b64 = encoded.split('$', 3)
        return {
            'algorithm': algorithm,
            'log_rounds': log_rounds,
            'salt': base64.b64decode(salt_b64).decode('utf-8'),
            'hash': mask_hash(hash_b64, show=2),
        }

    def must_update(self, encoded):
        algorithm, log_rounds, _, _ = encoded.split('$', 3)
        return int(log_rounds) != self.log_rounds
