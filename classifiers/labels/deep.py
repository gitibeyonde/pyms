import MySQLdb

 
dbs = MySQLdb.connect("mysql.ibeyonde.com","admin","1b6y0nd6","ibe" )
cursor = dbs.cursor()
main = {}
word = None
file_name = open('sublabels.txt')
for f in file_name:
    print main
    try:
        _ = int(f[0])
        g = f.split(',')
            
        for i in g:
            print i
            if '-' in i:
                i = i.split('-')
                print i[0]
                for j in range(int(i[0]),int(i[1])+1):
                     main[word].append(int(j))
            else:         
                main[word].append(int(i))
        
    except:
        if(f[0]==','):
            f = f[1:]
            g = f.split(',')
            
            for i in g:
                print i
                if '-' in i:
                    i = i.split('-')
                    print i[0]
                    for j in range(int(i[0]),int(i[1])+1):
                         main[word].append(int(j))
                else:         
                    main[word].append(int(i))
        else:
            f = f.split('-',1)
            word = f[0]
            main[word] = []
            g = f[1].split(',')
            
            for i in g:
                print i
                if '-' in i:
                    i = i.split('-')
                    print i[0]
                    for j in range(int(i[0]),int(i[1])+1):
                         main[word].append(int(j))
                else:         
                    main[word].append(int(i))    

i = 1
            
for category , labels in main.iteritems():
    
    cursor.execute('INSERT INTO SUBLABELS values (%s,%s)',(i,category))
    for k in labels:
        cursor.execute('UPDATE LABELS SET SUBLABEL = %s where ID = %s',(i,k))
    
    i = i + 1

dbs.commit()    
    
    
    
    
    
    
    
    
    
    
    
    
    
     