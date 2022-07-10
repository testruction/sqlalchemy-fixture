
# -*- coding: utf-8 -*-
import boto3
client = boto3.client('sts')
aws_account_id = client.get_caller_identity()['Account']

import os, argparse
# CLI arguments composition
parser = argparse.ArgumentParser()
parser.add_argument('--debug',
                    help='Enable debug logging',
                    action='store_true')
parser.add_argument('--trace-stdout',
                    help="Show OpenTelemetry output to console",
                    action="store_true")
parser.add_argument('--host',
                    type=str,
                    help='Hostname, fully qualified name or IP address',
                    default=os.environ.get('SNOWFLAKE_ENDPOINT', default=None))
parser.add_argument('--username',
                    type=str,
                    help='User login name',
                    default=os.environ.get('SNOWFLAKE_USER', default=None))
parser.add_argument('--password',
                    type=str,
                    help='User login password',
                    default=os.environ.get('SNOWFLAKE_PASSWORD', default=None))
parser.add_argument('--authenticator',
                    type=str,
                    help='Snowflake authenticator',
                    default=os.environ.get('SNOWFLAKE_AUTHENTICATOR', default=None))
parser.add_argument('--role',
                    type=str,
                    help='User role',
                    default=os.environ.get('SNOWFLAKE_ROLE', default=None))
parser.add_argument('--warehouse',
                    type=str,
                    help='Name of the warehouse',
                    default=os.environ.get('SNOWFLAKE_WAREHOUSE', default=None))
parser.add_argument('--database',
                    type=str,
                    help='Name of the database',
                    default=os.environ.get('SNOWFLAKE_DATABASE', default=None))
parser.add_argument('--schema',
                    type=str,
                    help='Name of the schema',
                    default=os.environ.get('SNOWFLAKE_SCHEMA', default=None))

# Initialize logging
from demo.logging import init_logger
init_logger(args)
# Initialize telemetry
from demo.telemetry import init_tracer
init_tracer(args)

from snowflake.sqlalchemy import URL

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_NABLED = True
    SITE_NAME = 'studiosd-webdemo'
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = URL(account = args.host,
                              user = args.username,
                              password = args.password,
                              role = args.role,
                              warehouse = args.warehouse,
                              database = args.database,
                              schema = args.schema,
                              authenticator = args.authenticator)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
