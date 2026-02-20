from app.core.security import decode_jwt, hash_password, make_jwt, verify_password


def test_password_hashing_argon2id():
    p = "super-secure-password"
    h = hash_password(p)
    assert verify_password(p, h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token, jti, _ = make_jwt("42", "access", 5, "secret", {"role": "ADMIN"})
    payload = decode_jwt(token, "secret")
    assert payload["sub"] == "42"
    assert payload["jti"] == jti
