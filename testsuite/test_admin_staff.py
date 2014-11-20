from flask import url_for
from pyquery import PyQuery

from mrt.models import Staff
from mrt.mail import mail
from .factories import StaffFactory, UserFactory, RoleUserFactory


PERMISSION = ('manage_staff', )


def test_staff_list(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION)
    StaffFactory(user__email='test@email.com')
    StaffFactory(user__email='another_test@email.com')

    client = app.test_client()
    with app.test_request_context():
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff')
        resp = client.get(url)

        table = PyQuery(resp.data)('#staff')
        tbody = table('tbody')
        row_count = len(tbody('tr'))
        assert row_count == 2


def test_staff_add(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION)
    data = StaffFactory.attributes()
    data['user-email'] = 'test@email.com'
    data['user-is_superuser'] = 'y'

    client = app.test_client()
    with app.test_request_context(), mail.record_messages() as outbox:
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff_edit')
        resp = client.post(url, data=data)
        assert len(outbox) == 1
        assert resp.status_code == 302
        assert Staff.query.count() == 1
        assert Staff.query.get(1).user.is_superuser is True


def test_staff_add_with_existing_user(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION)
    user = UserFactory(email='test@email.com')
    data = StaffFactory.attributes()
    data['user-email'] = user.email

    client = app.test_client()
    with app.test_request_context(), mail.record_messages() as outbox:
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff_edit')
        resp = client.post(url, data=data)
        assert len(outbox) == 0
        assert resp.status_code == 302
        assert Staff.query.count() == 1


def test_staff_add_fail_with_existing_staff(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION)
    staff = StaffFactory(user__email='test@email.com')
    data = StaffFactory.attributes()
    data['user-email'] = staff.user.email

    client = app.test_client()
    with app.test_request_context(), mail.record_messages() as outbox:
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff_edit')
        resp = client.post(url, data=data)
        assert len(outbox) == 0
        assert resp.status_code == 200
        assert Staff.query.count() == 1


def test_staff_edit(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION,
                                user__email='test@email.com')
    staff = StaffFactory()
    data = StaffFactory.attributes()
    data['user-email'] = data.pop('user')
    data['user-is_superuser'] = 'y'
    data['title'] = title = 'CEO'

    client = app.test_client()
    with app.test_request_context(), mail.record_messages() as outbox:
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff_edit', staff_id=staff.id)
        resp = client.post(url, data=data)
        assert resp.status_code == 302
        assert len(outbox) == 0
        assert staff.title == title
        assert staff.user.is_superuser is True


def test_staff_delete(app):
    role_user = RoleUserFactory(role__permissions=PERMISSION,
                                user__email='test@email.com')
    staff = StaffFactory()
    client = app.test_client()
    with app.test_request_context():
        with client.session_transaction() as sess:
            sess['user_id'] = role_user.user.id
        url = url_for('admin.staff_edit', staff_id=staff.id)
        resp = client.delete(url)

    assert resp.status_code == 200
    assert Staff.query.count() == 0
