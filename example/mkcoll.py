from pathlib import Path

import dlite

thisdir = Path(__file__).resolve().parent
dlite.storage_path.append(thisdir)

TypeOne = dlite.get_instance("http://onto-ns.com/meta/0.1/TypeOne")
TypeTwo = dlite.get_instance("http://onto-ns.com/meta/0.1/TypeTwo")
TypeThree = dlite.get_instance("http://onto-ns.com/meta/0.1/TypeThree")


inst1 = TypeOne(id="http://www.osp-core.com/cuds#f817bd09-3945-4325-9a60-62ecca19ea3c")
inst1.dpOne = "a"
inst1.dpTwo = 1

inst2a = TypeTwo(id="http://www.osp-core.com/cuds#7dc3081f-72cb-4754-9623-e821b352fd14")
inst2a.dpOne = "g"
inst2a.dpTwo = 4
inst2a.dpThree = 8.9

inst2b = TypeTwo(id="http://www.osp-core.com/cuds#db11661e-e815-4f36-b5a6-2bafe25f09b6")
inst2b.dpOne = "b"
inst2b.dpTwo = 5
inst2b.dpThree = 2.5

inst3 = TypeThree(
    id="http://www.osp-core.com/cuds#5c29896e-b51f-4994-903f-090a2dedbac3"
)
inst3.dpTwo = 3


coll = dlite.Collection()
coll.add("inst1", inst1)
coll.add("inst2a", inst2a)
coll.add("inst2b", inst2b)
coll.add("inst3", inst3)

# coll.add_relation(inst1.uri, "ex:opOne", inst2b.uri)
# coll.add_relation(inst1.uri, "ex:opTwo", inst3.uri)
# coll.add_relation(inst2a.uri, "ex:iOPTwo", inst2b.uri)
# coll.add_relation(inst2b.uri, "ex:iOPOne", inst1.uri)
# coll.add_relation(inst2b.uri, "ex:opTwo", inst2a.uri)
# coll.add_relation(inst3.uri, "ex:iOPTwo", inst1.uri)

coll.add_relation("inst1", "ex:opOne", "inst2b")
coll.add_relation("inst1", "ex:opTwo", "inst3")
coll.add_relation("inst2a", "ex:iOPTwo", "inst2b")
coll.add_relation("inst2b", "ex:iOPOne", "inst1")
coll.add_relation("inst2b", "ex:opTwo", "inst2a")
coll.add_relation("inst3", "ex:iOPTwo", "inst1")

# coll.save("yaml", "instances.yaml", "mode=w")
coll.save("json", "instances.json", "mode=w")
