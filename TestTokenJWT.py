# TestTokenJWT.py

from flask import Flask, request, jsonify
import jwt
import datetime

TestTokenJWT = Flask(__name__)

# Secret key untuk enkripsi JWT
TestTokenJWT.config['SECRET_KEY'] = 'jwtjwt123'

# Dummy data pengguna
users = {
    'user1': 'password1',
    'user2': 'password2'
}

@TestTokenJWT.route('/login', methods=['POST'])
def login():
    auth_data = request.json

    if not auth_data or not 'username' in auth_data or not 'password' in auth_data:
        return jsonify({'message': 'Could not veripyhfy'}), 401

    username = auth_data['username']
    password = auth_data['password']

    if username in users and users[username] == password:
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, TestTokenJWT.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

if __name__ == '__main__':
    TestTokenJWT.run(debug=True)