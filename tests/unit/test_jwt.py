from roamrs import _jwt as jwt

def test_jwt():
    j = jwt.JWTService('hello', ['HS256'])
    assert {"sub": "1234567890", "name": "John Doe", "iat": 1516239022} == j('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.ElsKKULlzGtesThefMuj2_a6KIY9L5i2zDrBLHV-e0M')
