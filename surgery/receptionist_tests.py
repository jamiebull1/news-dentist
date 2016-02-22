# -*- coding: utf-8 -*-
"""
"""
import os
import receptionist
import unittest
import tempfile


class ReceptionistTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, receptionist.app.config['DATABASE'] = tempfile.mkstemp()
        receptionist.app.config['TESTING'] = True
        self.app = receptionist.app.test_client()
        receptionist.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(receptionist.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No previous appointments' in rv.data

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert b'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert b'Invalid password' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            query='<Hello World>',
            depth=987
        ), follow_redirects=True)
        assert b'No queries here so far' not in rv.data
        assert b'&lt;Hello World&gt;' in rv.data
        assert b'/results/Hello_World.txt' in rv.data
        assert b'987' in rv.data

if __name__ == '__main__':
    unittest.main()
