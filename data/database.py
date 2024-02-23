import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SIGNUP_SUBJECT = os.getenv('SIGNUP_SUBJECT')
RESET_PASSWORD_SUBJECT = os.getenv('RESET_PASSWORD_SUBJECT')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


import ZODB, ZODB.FileStorage, transaction
import BTrees.OOBTree

from user import User

storage = ZODB.FileStorage.FileStorage('database.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

if not hasattr(root, "config"):
    root.config = BTrees.OOBTree.BTree()
if not hasattr(root, "user"):
    root.user = BTrees.OOBTree.BTree()
    root.config["currentUserID"] = 1
    root.user["0000000000000"] = User("0000000000000", ADMIN_USERNAME, SENDER_EMAIL, ADMIN_PASSWORD)
if not hasattr(root, "blog"):
    root.blog = BTrees.OOBTree.BTree()
    root.config["currentBlogID"] = 1
if not hasattr(root, "event"):
    root.event = BTrees.OOBTree.BTree()
    root.config["currentEventID"] = 1

transaction.commit()
