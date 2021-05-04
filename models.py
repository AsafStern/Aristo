from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from Workers import *
import mysql.connector
from mysql.connector import Error
from flask_login import UserMixin



app = Flask(__name__, template_folder='templates',
            static_folder=r'C:\Users\itay dar\Desktop\projects\tender\hello_flask\git checker\aristo\templates')
app.secret_key = "tenderly_secret_key"  # secret app for the session to keep data
app.permanent_session_lifetime = timedelta(minutes=10)  # time untill user forced to log out

'''
config the connection to mysql database
'''

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://itda:28031994@127.0.0.1:3306/aristodb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app,session_options={"autoflush": False})  # create connection with database



class User(UserMixin,db.Model):
    '''
        @Name : User
        @Do: create table that contain all the users and the relevant data about them in the database

        @ Param:
                first_name - user first name.
                last_name - user last name.
                email: user email address (must be validate by regular expression)
                password: user password. (must be validate by regular expression)
    '''

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    # todo references
    contact_user = db.relationship('Tender', backref=db.backref('User'), lazy=True)
    # manager_tender = db.relationship('Tender', backref=db.backref('User'), lazy=True)
    task = db.relationship('UserInTask', backref=db.backref('User'), lazy=True)
    file = db.relationship('FileInTask', backref=db.backref('User'), lazy=True)
    comment_in_task = db.relationship('TaskNote', backref=db.backref('User'), lazy=True)
    user_task_log = db.relationship('TaskLog', backref=db.backref('User'), lazy=True)
    user_notification = db.relationship('Notification',backref=db.backref('User'), lazy=True)
    task_owner_user = db.relationship('Task', backref=db.backref('User'), lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class Tender(db.Model):
    '''
        @Name : Tender
        @Do: create table that contain all the Tender and the relevant data about them in the database.
        @ Param:
                tid - tender indication number.
                protocol_number - tender protocol number (for government use).
                tenders_committee_Type - the area on which the tender rely to such as - ['רכישות','תקשוב','יועצים',...]
                procedure_type = the type of how the procedure occurs such as
                                    - ['מכרז פומבי','תיחור סגור','פנייה פומבית','RFI','מכרז חשכ"ל','הצעת מחיר',...]
                subject: tender subject.
                department: the departments that create the tender. can be - ['רווחה','מערכות מידע','לוגיסטיקה','לשכה משפטית ',...]
                start_date: tender start date
                finish_date: tender estimated finish date
                contact_user_from_department - reference to a user object from user table.
                procedure_number - the id of the procedure.
                tender_manager - the manager of the procedure (get's admin permission)
    '''

    __tablename__ = "Tenders"

    tid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    protocol_number = db.Column(db.VARCHAR(20))
    tenders_committee_Type = db.Column(db.VARCHAR(20))
    procedure_type = db.Column(db.VARCHAR(20))
    subject = db.Column(db.VARCHAR(250), nullable=False)
    department = db.Column(db.VARCHAR(50))
    start_date = db.Column(db.DateTime(255), nullable=False)
    finish_date = db.Column(db.DateTime(255), nullable=True)
    contact_user_from_department = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    tender_manager = db.Column(db.VARCHAR(50),nullable=False)
    # todo references
    task = db.relationship('Task', backref='Tender',cascade="all,delete", lazy=True)
    notification_in_tender = db.relationship('NotificationInTender',cascade="all,delete", backref='Tenders', lazy=True)


    def __init__(self, protocol_number, tenders_committee_Type, procedure_type, subject, department, start_date,
                 finish_date, contact_user_from_department, tender_manager):
        self.protocol_number = protocol_number
        self.tenders_committee_Type = tenders_committee_Type
        self.procedure_type = procedure_type
        self.subject = subject
        self.department = department
        self.start_date = start_date
        self.finish_date = finish_date
        self.contact_user_from_department = contact_user_from_department
        self.tender_manager = tender_manager


class Task(db.Model):
    """
    task_id = primary_key
    tid = tender id
    odt = open date time (removed from "blocked")
    deadline = needed to be done until
    finish = finished in actual fact
    status = ["open", "close", "blocked", "on progress"]
    subject = short text(50)
    description = longer text(120)
    """
    __tablename__ = "Tasks"
    task_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    tender_id = db.Column(db.Integer, db.ForeignKey("Tenders.tid"))
    task_owner_id = db.Column(db.Integer,db.ForeignKey("Users.id"))
    odt = db.Column(db.DateTime(255), nullable=False)
    deadline = db.Column(db.DateTime(255), nullable=False)
    finish = db.Column(db.DateTime(255))
    # status = db.Column(db.VARCHAR(50),db.CheckCostraint('status in ["open", "close", "blocked", "on progress"]'))  # todo
    status = db.Column(db.VARCHAR(50))
    subject = db.Column(db.VARCHAR(50))
    description = db.Column(db.VARCHAR(120))
    # todo references
    task_users = db.relationship('UserInTask', backref='Tasks',cascade="all,delete", lazy=True)
    task_logs = db.relationship('TaskLog', backref='Tasks',cascade="all,delete", lazy=True)
    task_notes = db.relationship('TaskNote', backref='Tasks',cascade="all,delete", lazy=True)
    task_files = db.relationship('FileInTask', backref='Tasks',cascade="all,delete", lazy=True)
    notification_in_tasks = db.relationship('NotificationInTask',cascade="all,delete", backref='Tasks', lazy=True)

    def __init__(self, tender_id,task_owner_id, odt, deadline, finish, status, subject, description):
        self.tender_id = tender_id
        self.task_owner_id = task_owner_id
        self.odt = odt
        self.deadline = deadline
        self.finish = finish
        self.status = status
        self.subject = subject
        self.description = description


class TaskLog(db.Model):
    """
    task_id = foreign key
    init_time= the time the log was created
    description = needed to be set and interpreted:
        user_id added u user_id = "נעה לוי הוסיפה את אבי כהן"
        user_id added f file_id = "נעה לוה הוסיפה קובץ למשימה"
        user_id edited description = "נעה לוי ערכה את תיאור המשימה"
        user_id changed status = "נעה לוי שינתה את סטטוס המשימה"
        ....
    """
    __tablename__ = "TasksLogs"

    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), primary_key=True)
    init_time = db.Column(db.DateTime(255), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("Tasks.task_id"))
    description = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self,user_id, task_id, init_time, description):
        self.user_id = user_id
        self.task_id = task_id
        self.init_time = init_time
        self.description = description


class TaskNote(db.Model):
    """
    description
    """
    __tablename__ = "TasksNotes"

    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), primary_key=True)
    time = db.Column(db.DateTime(255), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("Tasks.task_id"))
    note = db.Column(db.VARCHAR(120), nullable=False)

    def __init__(self, user_id, time, task_id, note):
        self.user_id = user_id
        self.time = time
        self.task_id = task_id
        self.note = note


class UserInTask(db.Model):
    '''
        @Name : UserInTask
        @Do: create table that contain for each user all the tasks that he is assign
        @ Param:
                task_id - user indication number.
                user_id - task id.
                Permissions - the user's premissions
    '''

    __tablename__ = "UsersInTasks"

    task_id = db.Column(db.Integer, db.ForeignKey('Tasks.task_id'), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True, nullable=False)
    # permissions = db.Column(db.Varchar(10),db.CheckCostraint('permissions in ["god","admin","editor","viewer"]'))
    permissions = db.Column(db.VARCHAR(10))

    def __init__(self, task_id, user_id, permissions):
        self.task_id = task_id
        self.user_id = user_id
        self.permissions = permissions


class FileInTask(db.Model):
    '''
        @Name : FilesInTasks
        @Do: for each file
        @ Param:
                file_id - file indication number.
                file_name - the name of the file
                file - the file itself - saved as largebinary.
                task_id = the task where the file publishd
                user_id - the user that published the task
    '''

    __tablename__ = "FilesInTasks"
    file_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    file_name = db.Column(db.VARCHAR(250))
    file_data = db.Column(db.LargeBinary)
    task_id = db.Column(db.Integer, db.ForeignKey('Tasks.task_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

    def __init__(self, file_id, file_name, file_data,task_id,user_id):
        self.file_id = file_id
        self.file_name = file_name
        self.file_data = file_data
        self.task_id = task_id
        self.user_id = user_id


class TaskDependency(db.Model):
    '''
        @Name : FilesInTasks
        @Do: for each file
        @ Param:
            blocked: the task that depend in other task.
            blocking: the task that block other task.
    '''

    __tablename__ = "TasksDependencies"

    blocked = db.Column(db.Integer, db.ForeignKey('Tasks.task_id'), primary_key=True, nullable=False)
    blocking = db.Column(db.Integer, db.ForeignKey('Tasks.task_id'), primary_key=True, nullable=False)

    def __init__(self, blocked, blocking):
        self.blocked = blocked
        self.blocking = blocking


class TenderTemplate(db.Model):
    '''
        @Name : TenderTemplate
        @Do: create table that contain all the Tender templates and the relevant data about them in the database.
        @ Param:
                tid - tender template indication number.
                tenders_committee_Type - the area on which the tender rely to such as - ['רכישות','תקשוב','יועצים',...]
                procedure_type = the type of how the procedure occurs such as
                                    - ['מכרז פומבי','תיחור סגור','פנייה פומבית','RFI','מכרז חשכ"ל','הצעת מחיר',...]
                department: the departments that create the tender. can be - ['רווחה','מערכות מידע','לוגיסטיקה','לשכה משפטית ',...]
    '''

    __tablename__ = "TendersTemplate"

    tid = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    tenders_committee_Type = db.Column(db.VARCHAR(20))
    procedure_type = db.Column(db.VARCHAR(20))
    department = db.Column(db.VARCHAR(50))
    # todo references
    tender_tasks = db.relationship('TaskDependenciesTemplate',backref='TendersTemplate',lazy=True)

    def __init__(self, tenders_committee_Type, procedure_type,department):
        self.tenders_committee_Type = tenders_committee_Type
        self.procedure_type = procedure_type
        self.department = department


class TaskTemplate(db.Model):
    """
    task_id = primary_key
    status = ["open", "close", "blocked", "on progress"]
    subject = short text(50)
    description = longer text(120)
    time_delta = the amount of days the task should take
    """

    __tablename__ = "TasksTemplate"
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.VARCHAR(15))
    subject = db.Column(db.VARCHAR(100))
    description = db.Column(db.VARCHAR(500))
    time_delta = db.Column(db.Integer)
    # todo references
    # depender = db.relationship("TaskDependenciesTemplate",backref="TasksTemplate",lazy=True)
    # dependee = db.relationship("TaskDependenciesTemplate",backref="TasksTemplate",lazy=True)

    # task_1 = db.relationship('TaskDependenciesTemplate',backref='TasksTemplate',lazy=True)

    def __init__(self, status, subject, description, time_delta):
        self.status = status
        self.subject = subject
        self.description = description
        self.time_delta = time_delta

class TaskDependenciesTemplate(db.Model):
    """
    depender - the task that's blocking the second task
    dependee - the task that depend on another task
    tender_id - the tender_template that contain the tasks
    """
    __tablename__ = "TasksDependenciesTemplate"
    depender_id = db.Column(db.Integer,db.ForeignKey('TasksTemplate.task_id'), primary_key=True,nullable=True)
    dependee_id = db.Column(db.Integer,db.ForeignKey('TasksTemplate.task_id'), primary_key=True,nullable=True)

    depender = db.relationship("TasksDependenciesTemplate", backref="user", uselist=False, foreign_keys=[person_user_id])

    tender_id = db.Column(db.Integer,db.ForeignKey('TendersTemplate.tid'), primary_key=True,nullable=False)

    def __init__(self, depender, dependee, tender_id):
        self.depender = depender
        self.dependee = dependee
        self.validate()
        self.tender_id = tender_id

    def validate(self):
        if self.dependee == self.depender:
            raise Exception

class Notification(db.Model):

    __tablename__ = "Notifications"
    nid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=True)
    status = db.Column(db.Boolean, default=False, nullable=False)
    subject = db.Column(db.VARCHAR(50))
    type = db.Column(db.VARCHAR(50))
    created_time = db.Column(db.DateTime(255))
    # todo references
    notification_in_tender = db.relationship('NotificationInTender',cascade="all,delete", backref='Notification', lazy=True)
    notification_in_task = db.relationship('NotificationInTask',cascade="all,delete", backref='Notification', lazy=True)


    def __init__(self,user_id,status,subject,type,created_time):
        self.user_id = user_id
        self.status = status
        self.subject = subject
        self.type = type
        self.created_time = created_time

class NotificationInTender(db.Model):

    __tablename__ = "NotificationsInTender"
    nid = db.Column(db.Integer,db.ForeignKey('Notifications.nid'), primary_key=True,nullable=False)
    tender_id = db.Column(db.Integer,db.ForeignKey('Tenders.tid'),primary_key=True,nullable=False)

    def __init__(self,nid,tender_id):
        self.nid = nid
        self.tender_id = tender_id

class NotificationInTask(db.Model):
    __tablename__ = "NotificationsInTask"
    nid = db.Column(db.Integer,db.ForeignKey('Notifications.nid'), primary_key=True,nullable=False)
    task_id = db.Column(db.Integer,db.ForeignKey('Tasks.task_id'),primary_key=True,nullable=False)

    def __init__(self,nid,task_id):
        self.nid = nid
        self.task_id = task_id


class ContactNote(db.Model):
    __tablename__ = "ContactNotes"
    note_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    msg = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime(255), nullable=False)

    def __init__(self,email,name,msg,date_created):
        self.email = email
        self.name = name
        self.msg = msg
        self.date_created = date_created






def get_db():
    return db

def get_app():
    return app

def get_my_sql_connection():
    try:
        connection = mysql.connector.connect(host="localhost",
                                             user="itda",
                                             passwd="28031994",
                                             database="aristodb")

        return connection
    except Error as e:
        print("error occurd")
        print(e)



if __name__ == '__main__':
    db = get_db()
    db.drop_all()
    db.create_all()
    # fill_db(30,db,User,Tender,Task,TaskLog,TaskNote,UserInTask)
    insert_tender_templates()
    insert_task_templates()
    insert_task_dependencies()


    # enter_fake_users_to_db(30,db,User)
    # enter_tenders_to_db(Tender,db,5)
    # enter_fake_tasks_to_db(Tender=Tender,Task=Task,db=db)

    # notification = Notification(1,"לא נקרא","איתי דר הוסיף אותך","הוספה")
    # try:
    #     db.session.add(notification)
    #     db.session.commit()
    # except Exception as e:
    #     print(e)





    # conn = get_my_sql_connection()
    # cursor = conn.cursor()
    # query = """select task_id from tasks
    #             order by task_id desc
    #             limit 1;
    #             """
    # cursor.execute(query)
    # print(cursor.fetchall()[0][0])



    # insert_data_to_dependencies()
    # try:
    #     # task_temp = TaskTemplate("חסום","הגשת בקשה להלוואה מבנקים","על מנת לרכוש את המטוסים יש לקבל הלוואות וערבויות מבנקים")
    #     tasks_relationship = TaskDependenciesTemplate(1,2,1)
    #     db.session.add(tasks_relationship)
    #     db.session.commit()
    # except Exception as e:
    #     print(e)
    # db.create_all()
    # fill_db(50,db,User,Tender,Task,TaskLog,TaskNote,UserInTask)
    # all_tenders_templates = TenderTemplate.query.all()
    # for temp in all_tenders_templates:



