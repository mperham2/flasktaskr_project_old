# test_tasks.py

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


    def create_task(self):
        return self.app.post('tasks/add/', data=dict(name='Go to the bank', due_date='02/05/2014', priority='1', posted_date='02/04/2014', status='1'), follow_redirects=True)

    def create_user_1(self):
        return self.register('Michael', 'michael@realpython.com', 'python', 'python')

    def create_user_2(self):
        return self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')

    def login_user_1(self):
        return self.login('Michael', 'python')

    def login_user_2(self):
        return self.login('Fletcher', 'python101')

    def create_admin_user(self):
        new_user=User(
                      name='Superman',
                      email='admin@realpython.com',
                      password=bcrypt.generate_password_hash('allpowerful'),
                      role='admin')
        db.session.add(new_user)
        db.session.commit()

########################
###### tasks tests ######
########################

    def test_logged_in_users_can_acces_tasks_page(self):
        # self.register(
        #               'Fletcher', 'fletcher@realpython.com', 'python', 'python')
        # self.login('Fletcher', 'python')
        self.create_user_1()
        self.login_user_1()
        response = self.app.get('tasks/tasks/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertIn('You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('New entry was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('Michael', 'michael@realpython', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.post('tasks/add/', data=dict(
                                 name = 'Go to the bank.',
                                 due_date='',
                                 priority='1',
                                 posted_date='02/05/2014',
                                 status='1'), follow_redirects=True)
        self.assertIn('This field is required', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertIn('The task was marked as complete. Nice.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user('Michael', 'michael@python.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("tasks/delete/1/", follow_redirects = True)
        self.assertIn('The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@python.com', 'python')
        self.login('Fletcher', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertNotIn('The task was marked as complete. Nice.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@python.com', 'python')
        self.login('Fletcher', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/delete/1/", follow_redirects=True)
        self.assertNotIn('The task was deleted. Why not add a new one?', response.data)

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertNotIn('That task belongs to another user.', response.data)

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/delete/1/", follow_redirects=True)
        self.assertNotIn('That task belongs to another user.', response.data)
        # self.assertIn('The task was deleted. Why not add a new one?', response.data)

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.create_user_1()
        self.login_user_1()
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user_2()
        response = self.login_user_2()
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertNotIn(
                'Mark as complete', response.data
        )
        self.assertNotIn(
                'Delete', response.data
        )

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.create_user_1()
        self.login_user_1()
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user_2()
        self.login_user_2()
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            'tasks/complete/2/', response.data
        )
        self.assertIn(
            'tasks/complete/2/', response.data
        )

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.create_user_1()
        self.login_user_1()
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
                'tasks/complete/1/', response.data
        )
        self.assertIn(
                'tasks/delete/1/', response.data
        )
        self.assertIn(
                'tasks/complete/2/', response.data
        )
        self.assertIn(
                'tasks/delete/2/', response.data
        )


if __name__ == "__main__":
    unittest.main()
