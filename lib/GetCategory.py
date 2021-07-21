import MySQLdb

def get_category(uuid):
    
    dbs = MySQLdb.connect("mysql.ibeyonde.com","admin","1b6y0nd6","ibe" )
    cursor = dbs.cursor()
    cursor.execute('select categories from camera_categories where uuid=%s',(uuid))            
    personal = cursor.fetchone()
    personal = personal[0]
    cursor.execute('select NAME from SUBLABELS where ID=%s',(personal))
    personal = cursor.fetchone()
    personal = personal[0]
    
    return {'label':personal}