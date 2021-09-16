import datetime

from sqlalchemy.orm import backref
from bapp import db

class Member(db.Model): 
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    member_fname = db.Column(db.String(255), nullable=False)
    member_lname = db.Column(db.String(255), nullable=False)
    member_email = db.Column(db.String(255), nullable=False)
    member_phone = db.Column(db.String(255), nullable=False)
    member_pwd = db.Column(db.String(255), nullable=False)
    member_pix = db.Column(db.String(255), nullable=False)
    member_dob = db.Column(db.DateTime(), nullable=True)
    reg_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    # favor = db.relationship("Favourites", back_populates="mem")


class Technology(db.Model):
    tech_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    tech_idname = db.Column(db.String(255), nullable=False)

    # tek = db.relationship("Favourites", back_populates="techfav")


class Favourites(db.Model):
    fav_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    fav_techid = db.Column(db.Integer(), db.ForeignKey('technology.tech_id'), nullable=False)
    fav_memberid = db.Column(db.Integer(), db.ForeignKey('member.id'), nullable=False)

    mem = db.relationship("Member", backref="favor")

    techfav = db.relationship("Technology", backref="tek")

class Contact(db.Model):
    contact_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    contact_name = db.Column(db.String(255))
    contact_message = db.Column(db.Text())




class States(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True) 
    name = db.Column(db.String(255))

class Local_governments(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_id = db.Column(db.Integer(), db.ForeignKey('states.id'))
    
    name = db.Column(db.String(255))

    state = db.relationship("States", backref="lgas")

class Transaction(db.Model):
    trx_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    trx_memberid = db.Column(db.Integer(),db.ForeignKey('member.id'), nullable=False)
    trx_amt = db.Column(db.Float(), nullable=False)
    trx_status = db.Column(db.String(40), nullable=False)
    trx_ref= db.Column(db.String(12), nullable=False)
    trx_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)    

    #set relationship
    user=db.relationship("Member",backref="usertrx")