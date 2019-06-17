import mysql.connector # pip3 install mysql-connector
from flask import redirect, Flask, request # pip3 install flask
import json
# import quickstart
# start virtual environment: .\env\Scripts\Activate
# deactivate virutal environment: deactivate

# use below command to access installed modules
# pip freeze

# Deploy a flask application on AWS
# https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80 

# 1. separate groups and members? add group then add member? or add group with member add?
# 2. choose machine learning algorithm
# 3. implement algorithm (train, model, predict)
# 4. deploy api

app = Flask(__name__)

# connect to mysql database
# change parameters as necessary
mydb = mysql.connector.connect(host="whynotworking.cyhofoocnvfm.us-east-1.rds.amazonaws.com", user="usernameMaster", passwd="password", database="DatabaseName")
mycursor = mydb.cursor()

# get information of all members in all groups
@app.route("/")
def get_all():
    objects_list = []
    mycursor.execute("select m.first_name, m.last_name, m.job, m.age, m.years, m.gender, "
        + "(select json_arrayagg(e.education) from education e where e.first_name = m.first_name and e.last_name = m.last_name), "
        + "(select json_arrayagg(i.interests) from interests i where i.first_name = m.first_name and i.last_name = m.last_name), "
        + "m.street, m.county, m.state, m.country, m.email, m.groups from member m order by m.last_name and m.groups")
    for i in mycursor:
        d = create_info_dict(i)
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

# get all groups
@app.route("/groups/")
def get_groups():
    objects_list = []
    mycursor.execute("select distinct groups from member")
    for i in mycursor:
        objects_list.append(i[0])
    j = json.dumps(objects_list)
    return j

# get information of all members in group
@app.route("/group/<string:group>/")
def get_group_mems(group):
    objects_list = []
    mycursor.execute("select m.first_name, m.last_name, m.job, m.age, m.years, m.gender, "
        + "(select json_arrayagg(e.education) from education e where e.first_name = m.first_name and e.last_name = m.last_name), "
        + "(select json_arrayagg(i.interests) from interests i where i.first_name = m.first_name and i.last_name = m.last_name), "
        + "m.street, m.county, m.state, m.country, m.email, m.groups from member m where groups = '" + group + "' order by m.last_name")
    for i in mycursor:
        d = create_info_dict(i)
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

# add one year to age and years for all members in group
@app.route("/group/<string:group>/add_year/")
def add_year(group):
    mycursor.execute("update member set age = age + 1, years = years + 1 where groups = '" + group + "'")
    mydb.commit()
    return redirect("/")

# get information of one member
@app.route("/<string:first_name>_<string:last_name>/")
def get_one(first_name, last_name):
    mycursor.execute("select m.first_name, m.last_name, m.job, m.age, m.years, m.gender, "
        + "(select json_arrayagg(e.education) from education e where e.first_name = m.first_name and e.last_name = m.last_name), "
        + "(select json_arrayagg(i.interests) from interests i where i.first_name = m.first_name and i.last_name = m.last_name), "
        + "m.street, m.county, m.state, m.country, m.email, m.groups from member m "
        + "where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    i = mycursor.fetchone()
    if i is not None:
        d = create_info_dict(i)
        j = json.dumps(d)
    else: j = json.dumps({})
    return j

# create dictionary from given member info
# used by get_all and get_one
def create_info_dict(i):
    d = {}
    d['first_name'] = i[0]
    d['last_name'] = i[1]
    d['job'] = i[2]
    d['age'] = i[3]
    d['years'] = i[4]
    d['gender'] = i[5]
    
    if i[6] is not None: d['education'] = json.loads(i[6])
    else: d['education'] = []
    if i[7] is not None: d['interests'] = json.loads(i[7])
    else: d['interests'] = []
    
    mylist = {}
    mylist['street'] = i[8]
    mylist['county'] = i[9]
    mylist['state'] = i[10]
    mylist['country'] = i[11]
    d['hometown'] = mylist
    
    d['email'] = i[12]
    d['group'] = i[13]
    return d

# count how many members
def count_mem():
    mycursor.execute("select count(*) from member")
    result = mycursor.fetchone()[0]
    return result

# education and interests are lists
# add new member information
@app.route("/", methods=['POST'])
def add_mem():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    job = request.form.get('job')
    age = request.form.get('age')
    years = request.form.get('years')
    gender = request.form.get('gender')
    education = list(filter(None, request.form.getlist('education')))
    interests = list(filter(None, request.form.getlist('interests')))
    street = request.form.get('street')
    county = request.form.get('county')
    state = request.form.get('state')
    country = request.form.get('country')
    email = request.form.get('email')
    group = request.form.get('group')

    mycursor.execute("insert into member values ('" + first_name + "', '" + last_name + "', '" + job 
        + "', " + age + ", " + years + ", '" + gender + "', '" + street + "', '" + county + "', '" 
        + state + "', '" + country + "', '" + email + "', '" + group + "')")
    if education is not None:
        for i in education:
            mycursor.execute("insert into education values ('" + first_name + "', '" + last_name + "', '" + i + "')")
    if interests is not None:
        for i in interests:
            mycursor.execute("insert into interests values ('" + first_name + "', '" + last_name + "', '" + i + "')")
    
    mydb.commit() # <-- all changes to database need commit

    return redirect("/" + first_name + "_" + last_name + "/")

# update member information
@app.route("/<string:first_name>_<string:last_name>/", methods=['POST'])
def update_mem(first_name, last_name):
    job = request.form.get('job')
    age = request.form.get('age')
    years = request.form.get('years')
    gender = request.form.get('gender')
    education = list(filter(None, request.form.getlist('education')))
    interests = list(filter(None, request.form.getlist('interests')))
    street = request.form.get('street')
    county = request.form.get('county')
    state = request.form.get('state')
    country = request.form.get('country')
    email = request.form.get('email')
    group = request.form.get('group')
    
    mycursor.execute("update member set job = '" + job + "', age =" + age + ", years = " + years 
        + ", gender = '" + gender + "', street = '" + street + "', county = '" + county + "', state = '" 
        + state + "', country = '" + country + "', email = '" + email + "', groups = '" + group 
        + "' where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    
    edu_dict = get_add_del_lists(get_item(first_name, last_name, 'education'), education)
    if edu_dict[0] is not None:
        for i in edu_dict[0]:
            mycursor.execute("insert into education values ('" + first_name + "', '" + last_name + "', '" + i + "')")
    if edu_dict[1] is not None:
        for i in edu_dict[1]:
            mycursor.execute("delete from education where first_name = '" + first_name + "' and last_name = '" + last_name + "' and education = '" + i + "'")
    
    i_dict = get_add_del_lists(get_item(first_name, last_name, 'interests'), interests)
    if i_dict[0] is not None:
        for i in i_dict[0]:
            mycursor.execute("insert into interests values ('" + first_name + "', '" + last_name + "', '" + i + "')")
    if i_dict[1] is not None:
        for i in i_dict[1]:
            mycursor.execute("delete from interests where first_name = '" + first_name + "' and last_name = '" + last_name + "' and interests = '" + i + "'")
    
    mydb.commit()
    return redirect("/" + first_name + "_" + last_name + "/")

# get education/interests information of member
def get_item(first_name, last_name, item):
    mycursor.execute("select json_arrayagg(" + item + ") from " + item + " where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    result = mycursor.fetchone()[0]
    return result

# determine differences between current and new lists
# add new items and delete missing ones
def get_add_del_lists(current, new):
    if current is not None:
        clist = json.loads(current)
    else: clist = []
    cset = set(clist)
    nset = set(new)
    add = [item for item in new if item not in cset]
    delete = [item for item in clist if item not in nset]
    return [add, delete]

# delete member information
@app.route("/<string:first_name>_<string:last_name>/", methods = ['DELETE'])
def delete_mem(first_name, last_name):
    mycursor.execute("delete from member where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    mycursor.execute("delete from education where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    mycursor.execute("delete from interests where first_name = '" + first_name + "' and last_name = '" + last_name + "'")
    mydb.commit()
    return redirect("/")

# for testing
@app.route("/testing/")
def test():
    # mycursor.execute("delete from education where name = 'Anna'")
    # mycursor.execute("insert into education values ('Anna', 'Carnegie Mellon')")
    # mycursor.execute("delete from interests where name = 'Anna'")
    # mycursor.execute("insert into interests values ('Anna', 'piano')")
    # mycursor.execute("alter table member add groups varchar(50)")
    # mydb.commit()
    
    # mycursor.execute("drop table member")
    # mycursor.execute("drop table education")
    # mycursor.execute("drop table interests")
    # mycursor.execute("create table member(first_name varchar(50), last_name varchar(50), job varchar(50), age int, years int, gender varchar(20), street varchar(50), county varchar(50), state varchar(50), country varchar(50), email varchar(50), groups varchar(50))")
    # mycursor.execute("create table education(first_name varchar(50), last_name varchar(50), education varchar(50))")
    # mycursor.execute("create table interests(first_name varchar(50), last_name varchar(50), interests varchar(50))")
    # mydb.commit()
    
    return get_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)