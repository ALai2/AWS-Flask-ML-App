import mysql.connector # pip3 install mysql-connector
from flask import redirect, Flask, request # pip3 install flask
import json
import quickstart
# start virtual environment: .\env\Scripts\Activate
# deactivate virutal environment: deactivate

# https://stackoverflow.com/questions/10434599/how-to-get-data-received-in-flask-request 
# http://flask.pocoo.org/docs/1.0/quickstart/

# 1. more columns? (First Name, Last Name, Company Name)
# 2. choose machine learning algorithm
# 3. implement algorithm (train, model, predict)
# 4. deploy api

app = Flask(__name__)

# connect to mysql database
# change parameters as necessary
mydb = mysql.connector.connect(host="whynotworking.cyhofoocnvfm.us-east-1.rds.amazonaws.com", user="usernameMaster", passwd="password", database="DatabaseName")
mycursor = mydb.cursor()

# get information of all members
@app.route("/")
def get_all():
    objects_list = []
    mycursor.execute("select m.name, m.job, m.age, m.years, m.gender, (select json_arrayagg(e.education) from education e where e.name = m.name), (select json_arrayagg(i.interests) from interests i where i.name = m.name), m.street, m.county, m.state, m.country, m.email from member m order by m.name")
    for i in mycursor:
        d = create_info_dict(i)
        objects_list.append(d)
    j = json.dumps(objects_list)
    return j

# get information of one member
@app.route("/<string:name>/")
def get_one(name):
    mycursor.execute("select m.name, m.job, m.age, m.years, m.gender, (select json_arrayagg(e.education) from education e where e.name = m.name), (select json_arrayagg(i.interests) from interests i where i.name = m.name), m.street, m.county, m.state, m.country, m.email from member m where name = '" + name + "'")
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
    d['name'] = i[0]
    d['job'] = i[1]
    d['age'] = i[2]
    d['years'] = i[3]
    d['gender'] = i[4]
    
    if i[5] is not None: d['education'] = json.loads(i[5])
    else: d['education'] = []
    if i[6] is not None: d['interests'] = json.loads(i[6])
    else: d['interests'] = []
    
    mylist = {}
    mylist['street'] = i[7]
    mylist['county'] = i[8]
    mylist['state'] = i[9]
    mylist['country'] = i[10]
    d['hometown'] = mylist
    
    d['email'] = i[11]
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
    name = request.form.get('name')
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

    mycursor.execute("insert into member values ('" + name + "', '" + job + "', " + age + ", " + years + ", '" + gender + "', '" + street + "', '" + county + "', '" + state + "', '" + country + "', '" + email + "')")
    if education is not None:
        for i in education:
            mycursor.execute("insert into education values ('" + name + "', '" + i + "')")
    if interests is not None:
        for i in interests:
            mycursor.execute("insert into interests values ('" + name + "', '" + i.lower() + "')")
    
    mydb.commit() # <-- all changes to database need commit

    return redirect("/" + name + "/")

# update member information
@app.route("/<string:name>/", methods=['POST'])
def update_mem(name):
    # update one by one by checking if not None?
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
    
    mycursor.execute("update member set job = '" + job + "', age =" + age + ", years = " + years + ", gender = '" + gender + "', street = '" + street + "', county = '" + county + "', state = '" + state + "', country = '" + country + "', email = '" + email + "' where name = '" + name + "'")
    
    edu_dict = get_add_del_lists(get_item(name, 'education'), education)
    if edu_dict[0] is not None:
        for i in edu_dict[0]:
            mycursor.execute("insert into education values ('" + name + "', '" + i + "')")
    if edu_dict[1] is not None:
        for i in edu_dict[1]:
            mycursor.execute("delete from education where name = '" + name + "' and education = '" + i + "'")
    
    i_dict = get_add_del_lists(get_item(name, 'interests'), interests)
    if i_dict[0] is not None:
        for i in i_dict[0]:
            mycursor.execute("insert into interests values ('" + name + "', '" + i + "')")
    if i_dict[1] is not None:
        for i in i_dict[1]:
            mycursor.execute("delete from interests where name = '" + name + "' and interests = '" + i + "'")
    
    mydb.commit()
    return redirect("/" + name + "/")

# get current education / interests information of member
def get_item(name, item):
    mycursor.execute("select json_arrayagg(" + item + ") from " + item + " where name = '" + name + "'")
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
@app.route("/<string:name>/", methods = ['DELETE'])
def delete_mem(name):
    mycursor.execute("delete from member where name = '" + name + "'")
    mycursor.execute("delete from education where name = '" + name + "'")
    mycursor.execute("delete from interests where name = '" + name + "'")
    mydb.commit()
    return redirect("/")

# https://towardsdatascience.com/designing-a-machine-learning-model-and-deploying-it-using-flask-on-heroku-9558ce6bde7b 
# @app.route("/train")
def ml_train():
    # future stuff
    return None

# @app.route("/model")
def ml_model():
    # future stuff
    return None

# prediction function
# import pickle
# def value_predict(to_predict_list):
#     to_predict = np.array(to_predict_list).reshape(1,12) # (1,12) number of columns
#     loaded_model = pickle.load(open("model.pkl","rb"))
#     result = loaded_model.predict(to_predict)
#     return result[0]

# @app.route("/predict", methods = ['POST'])
# def ml_predict():
#     to_predict_list = request.form.to_dict()
#     to_predict_list = list(to_predict_list.values())
#     to_predict_list = list(map(int, to_predict_list))
#     result = value_predict(to_predict_list)
#     # if condition
#     # prediction = ...
#     return json.dumps(prediction)

def add_event(mylist):
    quickstart.addevent(mylist)
    return redirect("/")

# for testing
@app.route("/testing/", methods=['POST'])
def test(): # (street, county, state, country)
    # mycursor.execute("delete from education where name = 'Anna'")
    # mycursor.execute("insert into education values ('Anna', 'Carnegie Mellon')")
    # mycursor.execute("delete from interests where name = 'Anna'")
    # mycursor.execute("insert into interests values ('Anna', 'piano')")
    # mycursor.execute("alter table member add email varchar(50)")
    # mydb.commit()
    
    names = list(filter(None, request.form.getlist('name')))
    dates = list(filter(None, request.form.getlist('date')))
    starts = list(filter(None, request.form.getlist('start')))
    ends = list(filter(None, request.form.getlist('end')))
    email1s = list(filter(None, request.form.getlist('email1')))
    email2s = list(filter(None, request.form.getlist('email2')))

    mylist = []
    for i in range(0, len(names)):
        d = {}
        d['name'] = names[i]
        d['date'] = dates[i]
        d['start'] = starts[i]
        d['end'] = ends[i]
        d['email1'] = email1s[i]
        d['email2'] = email2s[i]

        mylist.append(d)

    return add_event(mylist)
    # return None 

# print(test())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# alter table student add four varchar(20)
# alter table student drop column four
# mycursor.execute("select * from member where not name = 'Anna'")
# create table student(name varchar(20), college varchar(20));

# https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80 

# Data Matching
# https://www.talend.com/blog/2016/12/13/data-matching-101-how-does-data-matching-work/ 
# https://www.datasciencecentral.com/profiles/blogs/fuzzy-matching-algorithms-to-help-data-scientists-match-similar 
