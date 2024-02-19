
import ZODB, ZODB.FileStorage, transaction
import BTrees.OOBTree 

import persistent 
from persistent.list import PersistentList 

storage = ZODB.FileStorage.FileStorage('database.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

if not hasattr(root, "user"):
    root.user = BTrees.OOBTree.BTree()
    root.user["currentID"] = 0
if not hasattr(root, "post"):
    root.post = BTrees.OOBTree.BTree()
    root.post["currentID"] = 0
if not hasattr(root, "event"):
    root.event = BTrees.OOBTree.BTree()
    root.event["currentID"] = 0