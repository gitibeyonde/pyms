import MySQLdb

def LabelCategory(uuid,labels):
    myarray = []
    dbs = MySQLdb.connect("mysql.ibeyonde.com","admin","1b6y0nd6","ibe" )
    mainS = dbs.cursor()
    mainS.execute("select category from camera_manual where uuid=%s",(uuid))
    category = mainS.fetchall()
    for cat in category:
        myarray.append(int(cat[0]))
    print myarray    
    for label in labels:
        print label
        
        label = label.keys()
        label = label[0]
        mainS.execute("select SUBLABEL from LABELS where LABEL = %s ",(label))
        subcategory = mainS.fetchone()
        subcategory = subcategory[0]
        print subcategory
        if (subcategory in myarray):
            mainS.execute("select NAME from SUBLABELS where ID = %s ",(subcategory))
            subcategory = mainS.fetchone()
            subcategory = subcategory[0]
            
            return {'label':subcategory}
        
    return {'label':None}


    




