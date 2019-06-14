import database as db
from flask import Flask,render_template,request,redirect,url_for,session,flash
import demjson
# from core import corex
app=Flask(__name__)
app.secret_key="landalove"
@app.route('/',methods=['get','post'])
def public_home():
    return render_template('public/home.html')

@app.route('/login',methods=['get','post'])
def login():
    if 'login' in request.form:
        user=request.form['username']
        password=request.form['password']
        result=db.select("select * from login where username='%s' and password='%s'" % (user,password))
        if(len(result)>0):
            session['login_data']=result[0]
            if result[0]['login_type'] == "admin":
                return redirect(url_for('admin'))
            elif result[0]['login_type'] == "user":
                # flash('you were succesfully logged in')
                return redirect(url_for('user'))
            elif result[0]['login_type']=="institution":
                return redirect(url_for('insti_home'))
        else:
            flash('Invalid Login')
            return redirect(url_for('login'))

    return render_template("public/login.html",error_msg="failed")

@app.route('/logout',methods=['get','post'])
def logout():
    session.clear()
    return redirect(url_for('public_home'))

@app.route('/view_user',methods=['get','post'])
def view_user():

    if "delete" in request.args:
        id=request.args['id']
        res=db.delete("delete from user where login _id='%s'" % (id))
        res1 = db.delete("delete from login where login_id='%s'" % (id))
        print(res)
        if(res>0):
            res1 = db.select("select * from user")
            return render_template('admin/view_user.html',data=res1)

    if "login_id" in session['login_data']:
        res = db.select("select * from user")
        return render_template("admin/view_user.html",data=res)
    else:
        return redirect(url_for('public/login'))


@app.route('/registration',methods=['get','post'])
def registration():
    if 'submit' in request.form:
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        phone=request.form['phone']
        dob=request.form['dob']
        user=request.form['user']
        password=request.form['pass']
        cpassword = request.form['cpass']

        if(password==cpassword):
            loginid = db.insert("insert into login(username,password,login_type) values('%s','%s','user')" % (user, password))
            print( loginid)
            id=db.insert("insert into user(login_id,fname,lname,dob,email,phone) values('%s','%s','%s','%s','%s','%s')" % (loginid, fname, lname, dob, email, phone))
            if (id > 0):
                flash('User Registration Completed')
                print("success")
                return render_template("public/login.html")
            else:
                print("failed""")
                flash('user registration failed')

        else:
            flash('password and confirm password must be same')




    return render_template("public/registration.html")

@app.route('/update', methods=['get', 'post'])
def update():
    if "update" in request.form:
        id = request.form['id']
        fname = request.form['fname']
        lname = request.form['lname']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        q="update user set fname='%s',lname='%s',dob='%s',email='%s',phone='%s' where user_id='%s'" % (fname, lname, dob, email, phone, id)
        db.update(q)
        return redirect(url_for('view_user'))

    id = request.args['id']
    q = "select * from user where user_id='%s'" % (id)
    res = db.select(q)
    return render_template('admin/update.html', data=res)


@app.route('/admin',methods=['get','post'])
def admin():
    return render_template('admin/admin.html')


@app.route('/user',methods=['get','post'])
def user():
    if "submit" in request.form:
        marks = []
        for i in range(45):
            marks.append(0)
        q = "select count(*) as count from groups"
        count = db.select(q)[0]['count']
        groups = []
        for _ in range(count):
            groups.append(0)


        intrests = request.form.getlist('intrest')

        intr =  "(" + ",".join(intrests) + ")";

        q = "select distinct group_id from intrest_list where int_id in %s"% (intr)
        res = db.select(q)

        for row in res:
            groups[row['group_id']-1] = 1



        cou_id = request.form['cou_id']

        q = "select * from subject where cou_id='%s'" % cou_id
        res = db.select(q)
        for row in res:
            name  = "subject_" + str(row['sub_id'])
            if name in request.form:
                marks[row['sub_id']-1] = request.form[name]
            else:
                marks[row['sub_id'] - 1]=0
        input = marks + groups
        res = core.predict_course(input)
        return render_template('user/results.html',data = res)


    res=db.select("select * from course where cou_type='hsc'")
    intrest=db.select("select * from intrest_list")


    return render_template('user/user.html',data=res,intrest=intrest)


@app.route('/inst_mgmnt',methods=['get','post'])
def inst_mgmnt():
    if "submit" in request.form:

        uni=request.form['uni_id']
        cname=request.form['cname']
        ctype=request.form['caddr']
        email = request.form['email']
        phone = request.form['phone']

        s="insert into institution (uni_id,clg_name,ins_address,email,phone)values('%s','%s','%s','%s','%s')" %(uni,cname,ctype,email,phone)
        db.insert(s)
        flash('value added')

    res = db.select("select * from university inner join institution on institution.uni_id=university.uni_id")
    res1=db.select("select * from university")

    return render_template('admin/inst_mgmnt.html',university = res1,data=res)


@app.route('/crse_mgmnt',methods=['get','post'])
def crse_mgmnt():
    if "submit" in request.form:
        ins_id=request.form['clg_id']
        group_id=request.form['group_id']
        course_id = request.form['course']
        q="insert into college_course (ins_id,cou_id) values ('%s','%s')" % (ins_id,course_id)
        res=db.insert(q)
        flash('course added')

    q="select * from institution"
    inst=db.select(q)
    q = "select * from groups inner join course on course.group_id=groups.group_id"
    groups=db.select(q)
    res=db.select("select * from groups")
    res1 = db.select("select * from course")
    return render_template('admin/crse_mgmnt.html',inst=inst,groups = groups,data=res,course=res1)


@app.route('/get_subjects')
def get_subjects():
    cou_id = request.args['cou_id']
    q = "select * from subject where cou_id='%s'" % (cou_id)
    result = db.select(q)
    return demjson.encode(result)


@app.route('/get_institute')
def get_institute():
    loc_id = request.args['loc_id']
    q = "select * from institution where loc_id='%s'" % (loc_id)
    result = db.select(q)
    return demjson.encode(result)

@app.route('/get_course')
def get_course():
    ins_id = request.args['ins_id']
    q="select * from course where ins_id='%s'" % (ins_id)
    result=db.select(q)
    return demjson.encode(result)


@app.route('/subject',methods=['get','post'])
def subject():
    cor=session['course']
    if "submit" in request.form:
        q="select * from subject where cou_id='%s'" % (cor)
        res=db.select(q)

        marks= []
        for row in res:

            name = 'mark' + str(row['sub_id'])
            marks.append(request.form[name])


        return redirect(url_for('ability'))
    q="select * from subject where cou_id='%s'" % (cor)
    res=db.select(q)
    return render_template('user/subject.html',data=res)

# @app.route('/ability',methods=['get','post'])
# def ability():
#     return render_template('user/ability.html')

@app.route('/insti_reg',methods=['get','post'])
def insti_reg():
    if "submit" in request.form:
        name=request.form['name']
        univer=request.form['uni_id']
        add=request.form['address']
        email=request.form['email']
        phone=request.form['phone']
        user=request.form['user']
        passw = request.form['pass']
        cpassw = request.form['cpass']

        if(passw==cpassw):
            loginid = db.insert("insert into login(username,password,login_type) values('%s','%s','institution')" % (user, passw))
            print(loginid)
            r="insert into institution(uni_id,clg_name,ins_address,email,phone,login_id) values('%s','%s','%s','%s','%s','%s')"%(univer,name,add,email,phone,loginid)
            db.insert(r)
            if (r > 0):
                flash('Institution Registration Completed')
                print("success")
                return render_template("public/login.html")
            else:
                print("failed""")
                flash('Institution registration failed')
        else:
            flash('password and confirm password must be same')

    q="select * from university"
    res=db.select(q)
    return render_template('public/insti_reg.html',university=res)


@app.route('/insti_home',methods=['get','post'])
def insti_home():
    log_id = session['login_data']['login_id']
    res=db.select("select * from institution where login_id='%s'"%(log_id))
    return render_template('institution/insti_home.html',data=res)

@app.route('/upgrade_fec',methods=['get','post'])
def upgrade_fec():
    if "submit" in request.form:
        q = "select * from facilities"
        res = db.select(q)
        print (len(res))
        for row in res:
            print (row)
            fecility=request.form['feci'+str(row['fec_id'])]
            fec_id=row['fec_id']
            log_id=session['login_data']['login_id']
            q="SELECT ins_id FROM `institution` WHERE login_id='%s'" % log_id
            ins_id=db.select(q)[0]['ins_id']
            r="select * from insti_feci WHERE ins_id='%s' and fec_id='%s'" % (ins_id,fec_id)
            res1=db.select(r)
            if (len(res1) > 0):
                q="UPDATE insti_feci SET status='%s' WHERE ins_id='%s' and fec_id='%s'" %(fecility,ins_id,fec_id)
                db.update(q)
            else:
                q="insert into insti_feci(ins_id,fec_id,status) values('%s','%s','%s')" %(ins_id,fec_id,fecility)
                db.insert(q)
        return redirect(url_for('grade'))
    q="select * from facilities"
    res=db.select(q)

    return render_template('institution/upgrade_fec.html',data=res)

@app.route('/grade',methods=['get','post'])
def grade():
    log_id = session['login_data']['login_id']
    q="SELECT ins_id FROM `institution` WHERE login_id = '%s'"%(log_id)
    res=db.select(q)
    print(res)
    q="SELECT SUM*100/(SELECT COUNT(fec_id)FROM facilities) as rating FROM(SELECT COUNT(fec_id)as sum from insti_feci WHERE ins_id = '%s' AND(STATUS='yes' OR STATUS = 'not applicable'))tbl1"%(res[0]['ins_id'])

    res1=db.select(q)
    print (res1)
    if (res1[0]['rating']>80):
        r="update institution set grade='A' where ins_id='%s'" % (res[0]['ins_id'])
        db.insert(r)
    elif (res1[0]['rating']>60):
        r = "update institution set grade='B' where ins_id='%s'" % (res[0]['ins_id'])
        db.insert(r)
    elif (res1[0]['rating'] > 40):
        r = "update institution set grade='C' where ins_id='%s'" % (res[0]['ins_id'])
        db.insert(r)
    elif (res1[0]['rating'] > 20):
        r = "update institution set grade='D' where ins_id='%s'" % (res[0]['ins_id'])
        db.insert(r)
    else:
        r = "update institution set grade='E' where ins_id='%s'" % (res[0]['ins_id'])
        db.insert(r)

    q=db.select("select * from institution where login_id='%s'"%(log_id))

    return render_template('institution/grade.html',data=q)

@app.route('/ranking',methods=['get','post'])
def ranking():
    if "submit" in request.form:
        title=request.form['title']
        desc=request.form['desc']
        q="insert into facilities (title,description) values('%s','%s')" %(title,desc)
        res=db.insert(q)
        flash('value inserted')

    if "delete" in request.args:
        id=request.args['id']
        res=db.delete("delete from facilities where fec_id='%s'" % (id))
        flash('deleted succesfully')
    q="select * from facilities"
    res=db.select(q)
    return render_template('admin/ranking.html',data=res)

@app.route('/update_fec',methods=['get','post'])
def update_fec():
    id1=request.args['id']
    if "update" in request.form:
        id=request.form['id']
        title=request.form['title']
        desc=request.form['desc']
        q="update facilities set title='%s',description='%s' where fec_id='%s'" %(title,desc,id)
        db.update(q)
        return redirect(url_for('ranking'))
    q="select * from facilities where fec_id='%s'"%(id1)
    res=db.select(q)
    return render_template('admin/update_fec.html',data=res)

@app.route('/feedback_inst',methods=['get','post'])
def feedback_inst():
    if 'add' in request.form:
        fb=request.form['feedback']
        log_id = session['login_data']['login_id']
        print(log_id)
        log_type = session['login_data']['login_type']
        q = "select * from institution where login_id='%s' " % (log_id)
        res = db.select(q)
        print (res[0]['clg_name'])
        q="insert into feedback(login_id,login_type,name,feedback) values('%s','%s','(%s)','%s')" %(log_id,log_type,res[0]['clg_name'],fb)
        print(q)
        db.insert(q)
        flash('feedback sended')
    return render_template('institution/feedback_inst.html')

@app.route('/feedback_user',methods=['get','post'])
def feedback_user():
    if 'add' in request.form:
        fb=request.form['feedback']
        log_id = session['login_data']['login_id']
        print (log_id)
        log_type = session['login_data']['login_type']
        q="select * from user where login_id='%s' "%(log_id)
        res=db.select(q)
        print(res[0]['fname'])
        q="insert into feedback(login_id,login_type,name,feedback) values('%s','%s','%s','%s')" %(log_id,log_type,res[0]['fname'],fb)
        db.insert(q)
        flash('feedback sended')
    return render_template('user/feedback_user.html')

@app.route ('/feedback_admin',methods=['get','post'])
def feedback_admin():
    res=db.select("select * from feedback")
    print (res)
    return render_template('admin/feedback_admin.html',data=res)

app.run(debug=True,port=5002)