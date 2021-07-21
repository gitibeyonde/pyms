import Database_connect

dbs = Database_connect.dbs.cursor()
rows = open('../classifiers/labels/labels.txt')
classes = [r[r.find(" ") + 1:].split(",")[0] for r in rows]
new_classes = []
K = 1
for i in classes:
    i = i.strip('\n')
    i = i.strip('\r')
    dbs.execute('INSERT INTO LABELS (ID,LABEL,SUBLABEL) values (%s,%s,%s)',(K,i,0))
    K = K + 1
Database_connect.dbs.commit()    

    


