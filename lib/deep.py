from Utils import __ROOT__
import logging

def build_categories():

    main = {}
    word = None
    file_name = open(__ROOT__+'/classifiers/labels/sublabels.txt')
    
    for f in file_name:
        
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
                
    return main    