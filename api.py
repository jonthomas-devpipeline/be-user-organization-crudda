# 01. CRUDDA for users and organizations tables in the community database. Tables connected through keys.
# Make sure to create a community database before.

from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect("dbname='community' user='postgres' host='localhost' password='Jcmbtber1!'")
cursor = conn.cursor()

print("\nCreating Tables...\n")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Organizations (
        org_id SERIAL PRIMARY KEY,
        org_name VARCHAR NOT NULL,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR (4),
        type VARCHAR,
        active SMALLINT DEFAULT 1
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR,
        email VARCHAR UNIQUE NOT NULL,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR (4),
        active SMALLINT DEFAULT 1,
        org_id INTEGER REFERENCES Organizations (org_id) 
    );
""")

conn.commit()
print("Finished creating tables")

# Users

@app.route('/create/user', methods=['POST'])
def create_user():
    form = request.form
    first_name = form.get('first_name')
    if first_name == '':
        return jsonify('first_name is required!'), 400
    last_name = form.get('last_name')
    email = form.get('email')
    if email == '':
       return jsonify('email is required!')
    phone = form.get('phone')
    city = form.get('city')
    state = form.get('state')
    org_id = form.get('org_id')
    active = '1'
    cursor.execute('INSERT INTO users (first_name, last_name, email, phone, city, state, active, org_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (first_name, last_name, email, phone, city, state, active, org_id))
    conn.commit()
    return jsonify('User added'), 200

@app.route('/read/users')
def read_users():
    cursor.execute("SELECT * FROM users;")
    results = cursor.fetchall()

    if results:
        users = []
        for u in results:
            user_record = {
                'user_id':u[0],
                'first_name':u[1],
                'last_name':u[2],
                'email':u[3],
                'phone':u[4],
                'city':u[5],
                'state': u[6],
                'active':u[7],
                'org_id':u[8],
            }
            org_id_var = u[8]
            org_results = cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (str(org_id_var)))
            org_results = cursor.fetchone()

            if org_results:
                org_dict = {
                    'org_id': org_results[0],
                    'org_name': org_results[1],
                    'phone': org_results[2],
                    'city': org_results[3],
                    'state': org_results[4],
                    'type': org_results[5],
                    'active': org_results[6]
                }

            user_record['organization'] = org_dict
            users.append(user_record)
        return jsonify(users), 200
    
    return 'No users found', 404

@app.route('/read/user/<user_id>')
def read_user(user_id):
    results = cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id))
    results = cursor.fetchone()
    results_dict = {}

    if results:                      
        result_dict = {
            'user_id':results[0],
            'first_name': results[1],
            'last_name': results[2],
            'email': results[3],
            'phone': results[4],
            'city': results[5],
            'state': results[6],
            'active': results[7],
            'org_id': results[8]
        }  
        org_id_var = results[8]
        org_results = cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (str(org_id_var)))
        org_results = cursor.fetchone()

        if org_results:
            org_dict = {
                'org_id': org_results[0],
                'org_name': org_results[1],
                'phone': org_results[2],
                'city': org_results[3],
                'state': org_results[4],
                'type': org_results[5],
                'active': org_results[6]
            }

        result_dict['organization'] = org_dict
        return jsonify(result_dict), 200
    else:
        return jsonify(f"User {user_id} Not Found")

    
    
@app.route('/update/user/<user_id>', methods=['PUT', 'PATCH', 'POST'])
def update_user(user_id):
    form = request.form
    if form.get('first_name'):
        if form.get('first_name') == '':
            return jsonify('name is required!'), 400
        if form.get('first_name').isnumeric():
            return jsonify('first name must be a string')
    if form.get('last_name'):
        if form.get('last_name').isnumeric():
            return jsonify('last name must be a string')
    if form.get('email'):
        if form.get('email').isnumeric():
            return jsonify('email must be a string')
    if form.get('phone'):
        if 10 > len(form.get('phone')) > 10:
            return jsonify('phone number must be 10 digits'), 400
    if form.get('state'):
        if form.get('state').isnumeric():
            return jsonify('state must be a two character string')
    if form.get('active'):
        if 0 > int(form.get('active')) > 1:
            return jsonify('active must be 0 for inactive or 1 for active') 

    if form.get('first_name'):
        cursor.execute("UPDATE users SET first_name=%s WHERE user_id=%s", (form["first_name"], user_id))
        conn.commit()
    if form.get('last_name'):
        cursor.execute("UPDATE users SET last_name=%s WHERE user_id=%s", (form["last_name"], user_id))
        conn.commit()
    if form.get('email'):
        cursor.execute("UPDATE users SET email=%s WHERE user_id=%s", (form["email"], user_id))
        conn.commit()
    if form.get('phone'):
        cursor.execute("UPDATE users SET phone=%s WHERE user_id=%s", (form["phone"], user_id))
        conn.commit()
    if form.get('city'):
        cursor.execute("UPDATE users SET city=%s WHERE user_id=%s", (form["city"], user_id))
        conn.commit()
    if form.get('state'):
        cursor.execute("UPDATE users SET state=%s WHERE user_id=%s", (form["state"], user_id))
        conn.commit()
    if form.get('active'):
        cursor.execute("UPDATE users SET active=%s WHERE user_id=%s", (form["active"], user_id))
        conn.commit()   
    return jsonify('All provided fields were updated.')

@app.route('/delete/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id))
    results = cursor.fetchone()
    
    if not results:
        return (f"Team {user_id} not found."), 404

    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id))
    conn.commit()

    return (f" Team {user_id} Deleted"), 200

@app.route('/deactivate/user/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def deactivate_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id))
    results = cursor.fetchone()

    if not results:
        return (f"Team {user_id} not found."), 404
    
    cursor.execute("UPDATE users SET active=0 WHERE user_id=%s;", (user_id))
    conn.commit()

    return(f"Team {user_id} Deactivated"), 200

@app.route('/activate/user/<user_id>', methods=['POST', 'PATCH', 'PUT'])
def activate_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id))
    results = cursor.fetchone()

    if not results:
        return (f"Team {user_id} not found."), 404
    
    cursor.execute("UPDATE users SET active=1 WHERE user_id=%s;", (user_id))
    conn.commit()

    return(f"Team {user_id} Activated"), 200

# Organizations

@app.route('/create/org', methods=['POST'])
def create_org():
    form = request.form
    org_name = form.get('org_name')
    if org_name == '':
        return jsonify('org_name is required!')
    phone = form.get('phone')
    city = form.get('city')
    state = form.get('state')
    type = form.get('type')
    active = '1'
    cursor.execute('INSERT INTO organizations (org_name, phone, city, state, type) VALUES (%s, %s, %s, %s, %s)', (org_name, phone, city, state, type))
    conn.commit()
    return jsonify(f'Organization {org_name} added'), 200

@app.route('/read/orgs')
def read_orgs():
    cursor.execute("SELECT * FROM organizations;")
    results = cursor.fetchall()

    if results:
        orgs = []
        for u in results:
            org_record = {
                'org_id':u[0],
                'org_name':u[1],
                'phone':u[2],
                'city':u[3],
                'state': u[4],
                'type': u[5],
                'active':u[6]
            }
            orgs.append(org_record)
        return jsonify(orgs), 200
    
    return 'No orgs found', 404

@app.route('/read/org/<org_id>')
def read_org(org_id):
    results = cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (org_id))
    results = cursor.fetchone()
    if results:                      
        result_dictionary = {
            'org_id':results[0],
            'org_name': results[1],
            'phone': results[2],
            'city': results[3],
            'state': results[4],
            'type': results[5],
            'active': results[6]
        }  
        return jsonify(result_dictionary), 200
    else:
        return jsonify(f"Org {org_id} Not Found")

@app.route('/update/org/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def update_org(org_id):
    form = request.form
    if form.get('org_name'):
        if form.get('org_name').isnumeric():
            return jsonify('org_name name must be a string')
    if form.get('phone'):
        if 10 > len(form.get('phone')) > 10:
            return jsonify('phone number must be 10 digits'), 400
    if form.get('state'):
        if form.get('state').isnumeric():
            return jsonify('state must be a two character string')
    if form.get('type'):
        if form.get('type').isnumeric():
            return jsonify('type must be a string')
    if form.get('active'):
        if 0 > int(form.get('active')) > 1:
            return jsonify('active must be 0 for inactive or 1 for active') 

    if form.get('org_name'):
        cursor.execute("UPDATE organizations SET org_name=%s WHERE org_id=%s", (form["org_name"], org_id))
        conn.commit()
    if form.get('phone'):
        cursor.execute("UPDATE organizations SET phone=%s WHERE org_id=%s", (form["phone"], org_id))
        conn.commit()
    if form.get('city'):
        cursor.execute("UPDATE organizations SET city=%s WHERE org_id=%s", (form["city"], org_id))
        conn.commit()
    if form.get('state'):
        cursor.execute("UPDATE organizations SET state=%s WHERE org_id=%s", (form["state"], org_id))
        conn.commit()
    if form.get('type'):
        cursor.execute("UPDATE organizations SET type=%s WHERE org_id=%s", (form["type"], org_id))
        conn.commit()
    if form.get('active'):
        cursor.execute("UPDATE organizations SET active=%s WHERE org_id=%s", (form["active"], org_id))
        conn.commit()   
    return jsonify('All provided fields were updated for Organization {org_id}.')

@app.route('/delete/org/<org_id>', methods=['DELETE'])
def delete_org(org_id):
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (org_id))
    results = cursor.fetchone()
        
    if not results:
        return (f"Team {org_id} not found."), 404

    cursor.execute("DELETE FROM organizations WHERE org_id=%s", (org_id))
    conn.commit()

    return (f"Organization {org_id} Deleted"), 200

@app.route('/deactivate/org/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_org(org_id):
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (org_id))
    results = cursor.fetchone()

    if not results:
        return (f"Organization {org_id} not found."), 404
    
    cursor.execute("UPDATE organizations SET active=0 WHERE org_id=%s;", (org_id))
    conn.commit()

    return(f"Organization {org_id} Deactivated"), 200

@app.route('/activate/org/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def activate_org(org_id):
    cursor.execute("SELECT * FROM organizations WHERE org_id=%s", (org_id))
    results = cursor.fetchone()

    if not results:
        return (f"Organizations {org_id} not found."), 404
    
    cursor.execute("UPDATE organizations SET active=1 WHERE org_id=%s;", (org_id))
    conn.commit()

    return(f"Team {org_id} Activated"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086)
