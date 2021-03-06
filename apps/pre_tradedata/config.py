import requests
from microservices_connector.Interservices import Microservice, SanicApp, timeit, Friend
from configparser import ConfigParser
import click
import os,json
from flask import jsonify,request
import datetime
from ..initdb import Base, engine, db_session
from celery import Celery
from celery.schedules import crontab
# enviroment = 'ENV'

# import config from file
config = ConfigParser()
config.read('config.env')

Micro = Microservice(__name__)
app = Micro.app
app.config['CELERY_BROKER_URL'] = config["ENV"]['CELERY_BROKER_URL']
app.config['result_backend'] = config["ENV"]['result_backend']
app.config['SQLALCHEMY_DATABASE_URI'] = config["ENV"]['database']

celery = Celery(app.name, backend=app.config['result_backend'], broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@Micro.app.route('/')
def helloworld():
    return 'Hello World'
    
@Micro.app.route('/pre-trade/confirm-connect', methods=['POST'])
def confirm_connect():
    # print("data"+json.dumps(request))
    return jsonify({"log":"ok"})


def init_db():
    """Initiate all database. This should be use one time only
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from . import models
    Base.metadata.create_all(bind=engine)

# command line to start project


@click.command()
@click.option('--env', default='pre_trade_data', help='Setup enviroment variable.')
def main(env='env'):
    """Running method for Margin call app
    
    Keyword Arguments:
        env {str} -- Can choose between initdb, PROD, or ENV/nothing. 'initdb' will create database table and its structures, use onetime only .PROD only change debug variable in webapp to true (default: {'ENV'})
    """
    if env == 'initdb':
        init_db()
    else:
        env = str(env)
        debug = bool(config[env]['debug'] == 'True')
        Micro.run(host=config[env]['host'], port=int(
            config[env]['port']), debug=debug)
