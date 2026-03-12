import app
import sqlite3
import os

def create_test_user():
    print("Creating test user...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id=1')
    cursor.execute('INSERT INTO users (id, name, email, password, class_level, board) VALUES (?, ?, ?, ?, ?, ?)',
                   (1, 'Test User', 'test@edugalaxy.com', 'pbkdf2:sha256:260000$test', 'Class 4', 'CBSE'))
    conn.commit()
    conn.close()

def test_routes():
    print("Testing routes...")
    with app.app.test_request_context():
        # Mock session
        with app.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['user_name'] = 'Test User'
                sess['user_email'] = 'test@edugalaxy.com'
            
            # Test Home
            print("Testing /")
            res = client.get('/')
            print(f"Status: {res.status_code}")
            
            # Test Dashboard
            print("Testing /dashboard")
            res = client.get('/dashboard')
            print(f"Status: {res.status_code} -> {res.location if res.location else 'Direct'}")
            if res.status_code == 500:
                print(res.data[:500])

            # Test Learn Hub
            print("Testing /learn")
            res = client.get('/learn')
            print(f"Status: {res.status_code} -> {res.location if res.location else 'Direct'}")

            # Test Interactive Learn
            print("Testing /learn/interactive?subject=math")
            res = client.get('/learn/interactive?subject=math')
            print(f"Status: {res.status_code} -> {res.location if res.location else 'Direct'}")

if __name__ == '__main__':
    create_test_user()
    test_routes()
