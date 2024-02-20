import os
from dotenv import load_dotenv

load_dotenv(os.path.dirname(os.path.abspath(__file__)) + '\.env')

admin_username = os.getenv('ADMIN_USERNAME')
admin_password = os.getenv('ADMIN_PASSWORD')
sender_email = os.getenv('SENDER_EMAIL')
signup_subject = os.getenv('SIGNUP_SUBJECT')
reset_password_subject = os.getenv('RESET_PASSWORD_SUBJECT')
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')


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
    root.user["0000000000000"] = User("0000000000000", admin_username, sender_email, admin_password)
if not hasattr(root, "post"):
    root.post = BTrees.OOBTree.BTree()
    root.config["currentPostID"] = 1
if not hasattr(root, "event"):
    root.event = BTrees.OOBTree.BTree()
    root.config["currentEventID"] = 1

transaction.commit()