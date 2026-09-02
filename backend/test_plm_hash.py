import hashlib

stored_salt = "c3580e8d435d2bca0a1ea630fb3573342a1aa92299550d1b1b554f3b18671b5c"
stored_hash = "6026ec77deb7c3583114b82b0301d27661c002ae40b7d1fbdbab679c1c83d1ad05a62c7d22c58f103d57ab8ccaeee304cfa6cb0bd8a29a4fcfecf9e2ff55d7ea46d4297d255fe98f1afd070a835c967570dbc833ddb10f606e07ced6375e934da5c83e2ad169876e768ce9cb11e710772097ee3dc4317d7b289e16a811b9cd966dc01c4b841e43699649535d4a4866686ed3075b21705036af1b1234a34852ce05761e582486ca5d00e7ed2aa06453561f91fdf7abf38d84fe8559b70ae9ce4eb1a5666071b986c735942fba01f940cb34ebcc7d7454b2ee3bfdca36bb9a8771ee0c14f175c3d61be216f779a3426b66427ed80671b8799aa2ff216c2b9d91c3806b10a046a0cee3651a72571f7531dbfd8e88ab64533f0ba77184bd0aed55432c0b02012a8b7f3f701ef1dd1f0765b985e3c08d107b5cc04f173a7109a1c230df769ba63dd185b669fa7bac41cca6c7d15e8d11560e71c6a60ee559a92edf97dbc847b3f9e7596f210edb4ad27df9cdb1b5902d726af4c7b97903da1b2fa7b18dfa985ead763e9e25f1be8f2b3febca276958e765797eb7ddb3a9c6b00c8466f8152ccc4cc0b26f9070dca0dac3752e5a79dcc3eeec27307a717bff1030cc7c0eef8a66a6b96b64ea30933088e60aba35a117f12af0ce361dbc4155f71744c1caacc6630a10f04de2f56d3ceb8c9dd5de0dfb218ae54af28a235d3d5e0b3d48"

test_passwords = [
    "Shrinath@123456",
    "Shrinath@123",
    "Shrinath123456",
    "Shrinath123",
    "123456",
    "rajputshrinath349",
    "Shrinath_Rajput",
    "shrinath"
]

for p in test_passwords:
    h = hashlib.pbkdf2_hmac('sha512', p.encode('utf-8'), stored_salt.encode('utf-8'), 25000, 512).hex()
    if h == stored_hash:
        print(f"MATCH (salt as utf8 str): '{p}'")
    
    h2 = hashlib.pbkdf2_hmac('sha512', p.encode('utf-8'), bytes.fromhex(stored_salt), 25000, 512).hex()
    if h2 == stored_hash:
        print(f"MATCH (salt as hex bytes): '{p}'")

    h3 = hashlib.pbkdf2_hmac('sha1', p.encode('utf-8'), stored_salt.encode('utf-8'), 25000, 512).hex()
    if h3 == stored_hash:
        print(f"MATCH sha1 (salt as utf8 str): '{p}'")

    h4 = hashlib.pbkdf2_hmac('sha1', p.encode('utf-8'), bytes.fromhex(stored_salt), 25000, 512).hex()
    if h4 == stored_hash:
        print(f"MATCH sha1 (salt as hex bytes): '{p}'")
