# test_users.py

import os
import unittest

from project import app, db, bcrypt
from config import basedir
from project.models import Task, User

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    ##########################
    #### setup and teardown ##
    ##########################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.drop_all()

#############################
##### helper functions ######
#############################

    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

    def login(self, name, password):
        return self.app.post('users/', data=dict(
                             name=name, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('users/logout/', follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('users/register/', data=dict(name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

    def create_user_1(self):
        return self.register('Michael', 'michael@realpython.com', 'python', 'python')

    def create_user_2(self):
        return self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')


    def login_user_1(self):
        self.login('Michael', 'python')

    def login_user_2(self):
        self.login('Fletcher', 'python101')

    def create_admin_user(self):
        new_user=User(
                      name='Superman',
                      email='admin@realpython.com',
                      password=bcrypt.generate_password_hash('allpowerful'),
                      role='admin')
        db.session.add(new_user)
        db.session.commit()



#############################
##### user tests       ######
#############################

    def test_can_create_admin_user(self):
        new_user=User(
                      name='Superman',
                      email='admin@realpython.com',
                      password='allpowerful',
                      role='admin')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "Superman" and t.role == 'admin'


    # each test should start with 'test'
    def test_user_setup(self):
        new_user = User("mike01", "mike01@mike.com", "mikeperham")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "mike01"


    def test_form_is_present_on_login_page(self):
        response = self.app.get('users/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please sign in to access your task list', response.data)


    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn('Invalid username or password.', response.data)


    def test_users_can_login(self):
        self.create_user_1()
        # self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn('You are logged in. Go crazy.', response.data)

    def test_invalid_form_data(self):
        self.create_user_1()
        # self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn('Invalid username or password.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('users/register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please register to start a task list',
                      response.data)

    def test_duplicate_user_registration_throws_error(self):
        self.app.get('users/register/', follow_redirects=True)
        response = self.create_user_1()
        # self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.app.get('users/register/', follow_redirects=True)
        response = self.create_user_1()
        # self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn('Oh no! That username and/or email already exist.', response.data)

    def test_user_registration_field_errors(self):
        response = self.register(
                'Michael', 'michael@python.com', 'python', '')
        self.assertIn('This field is required.', response.data)


    def test_logged_in_users_can_logout(self):
        self.create_user_2()
        # self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        response = self.logout()
        self.assertIn('You are logged out. Bye.', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn('You are logged out. Bye.', response.data)

    def test_default_user_role(self):
        db.session.add(
                    User(
                        "Mike",
                       "Mike@mike.com",
                       "mikes"
                   )
        )
        db.session.commit()
        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEquals(user.role, 'user')

    def test_task_template_displays_logged_in_user_name(self):
        self.create_user_2()
        self.login_user_2()
        response = self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertIn('Fletcher', response.data)

    def test_404_error(self):
        response = self.app.get('/this-route-does-not-exist/')
        self.assertEquals(response.status_code, 404)
        self.assertIn('Sorry that page does not exist.', response.data)

    # def test_500_error(self):
    #     bad_user = User(
    #             name = 'Jeremy',
    #             email = 'jeremy@realpython.com',
    #             password = 'django'
    #     )
    #     db.session.add(bad_user)
    #     db.session.commit()
    #     response = self.login('Jeremy', 'django')
    #     self.assertEquals(response.status_code, 500)
    #     self.assertNotIn('ValueError: Invalid salt', response.data)
    #     self.assertIn('Something went terribly wrong.', response.data)


if __name__ == "__main__":
    unittest.main()
