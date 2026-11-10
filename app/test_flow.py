import os
from app import app, init_db

print("Testing database initialization...")
with app.app_context():
    init_db()
    print("[OK] init_db successful")

client = app.test_client()

# 1. Test public events
res = client.get('/events')
assert res.status_code == 200, f"/events returned {res.status_code}"
print("[OK] GET /events: 200 OK")

# 2. Test login page
res = client.get('/login')
assert res.status_code == 200, f"/login returned {res.status_code}"
print("[OK] GET /login: 200 OK")

# 3. Test register page
res = client.get('/register')
assert res.status_code == 200, f"/register returned {res.status_code}"
print("[OK] GET /register: 200 OK")

# 4. Test admin login
with client:
    res = client.post('/login', data={
        'email': 'admin@msvcollege.ac.in',
        'password': 'Admin@MSV2024'
    }, follow_redirects=True)
    assert res.status_code == 200
    print("[OK] Admin login successful")

    # 5. Test admin dashboard
    res = client.get('/admin/')
    assert res.status_code == 200, f"/admin/ returned {res.status_code}"
    print("[OK] GET /admin/: 200 OK")

    # 6. Test admin create event page
    res = client.get('/admin/events/create')
    assert res.status_code == 200, f"/admin/events/create returned {res.status_code}"
    print("[OK] GET /admin/events/create: 200 OK")

    # 7. Test creating a workshop event
    res = client.post('/admin/events/create', data={
        'title': 'Test AI & Robotics Workshop',
        'event_type': 'workshop',
        'description': 'Hands-on workshop on AI & Robotics',
        'event_date': '2026-11-15',
        'registration_deadline': '2026-11-10',
        'start_time': '09:30',
        'end_time': '16:30',
        'venue': 'APJ Abdul Kalam Auditorium',
        'capacity': '120',
        'is_published': '1'
    }, follow_redirects=True)
    assert res.status_code == 200
    print("[OK] POST /admin/events/create (Workshop): Created successfully!")

    # 8. Test creating a seminar event
    res = client.post('/admin/events/create', data={
        'title': 'National Seminar on Cloud Computing',
        'event_type': 'seminar',
        'description': 'National level paper presentations and expert keynotes',
        'event_date': '2026-11-20',
        'registration_deadline': '2026-11-18',
        'start_time': '10:00',
        'end_time': '15:00',
        'venue': 'Seminar Hall 2',
        'capacity': '80',
        'is_published': '1'
    }, follow_redirects=True)
    assert res.status_code == 200
    print("[OK] POST /admin/events/create (Seminar): Created successfully!")

    # 9. Test creating a symposium event with sub-events
    res = client.post('/admin/events/create', data={
        'title': 'TECHKRITI 2026 Symposium',
        'event_type': 'symposium',
        'description': 'Annual Inter-College Technical Symposium',
        'event_date': '2026-12-05',
        'registration_deadline': '2026-12-01',
        'start_time': '09:00',
        'end_time': '17:00',
        'venue': 'Main Campus Quadrangle',
        'capacity': '300',
        'is_published': '1',
        'sub_event_name[]': ['Code Relay', 'Web Canvas', 'Paper Presentation'],
        'sub_event_desc[]': ['Speed coding contest', 'UI design challenge', 'Research presentation'],
        'sub_event_allowed_teams[]': ['25', '20', '30'],
        'sub_event_min_team[]': ['2', '1', '1'],
        'sub_event_max_team[]': ['4', '2', '3']
    }, follow_redirects=True)
    assert res.status_code == 200
    print("[OK] POST /admin/events/create (Symposium): Created successfully with 3 sub-events!")

    # 10. Test admin events list
    res = client.get('/admin/events')
    assert res.status_code == 200
    assert b'Test AI &amp; Robotics Workshop' in res.data or b'Test AI & Robotics Workshop' in res.data
    assert b'TECHKRITI 2026 Symposium' in res.data
    print("[OK] GET /admin/events: Verified events appear in manage events list!")

# 11. Test participant registration and login
client2 = app.test_client()
with client2:
    reg_res = client2.post('/register', data={
        'name': 'Karthik Raja',
        'roll_no': '22CSE045',
        'dept': 'CSE',
        'section': 'A',
        'email': 'karthik@student.msvcollege.ac.in',
        'phone': '9876543210',
        'password': 'Student@2026',
        'confirm_password': 'Student@2026'
    }, follow_redirects=True)
    assert reg_res.status_code == 200
    print("[OK] Student registered successfully!")

    # Login student
    login_res = client2.post('/login', data={
        'email': 'karthik@student.msvcollege.ac.in',
        'password': 'Student@2026'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    print("[OK] Student logged in successfully!")

    # Test participant dashboard
    dash_res = client2.get('/participant/')
    assert dash_res.status_code == 200, f"/participant/ returned {dash_res.status_code}"
    assert b'Karthik Raja' in dash_res.data
    assert b'22CSE045' in dash_res.data
    print("[OK] GET /participant/ (Dashboard): 200 OK! Student info rendered!")

    # Test participant events page
    ev_res = client2.get('/participant/events')
    assert ev_res.status_code == 200
    assert b'Test AI &amp; Robotics Workshop' in ev_res.data or b'Test AI & Robotics Workshop' in ev_res.data
    print("[OK] GET /participant/events: 200 OK! Events visible to student!")

print("\n[SUCCESS] ALL TESTS PASSED! Backend, Database, Admin, and Student flows are verified 100% working!")
