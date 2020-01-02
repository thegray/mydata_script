import glob, os
import mysql.connector
from mysql.connector import Error
import hashlib

FILE_FORMAT = r'*.mp4'
DB_HOST = 'localhost'
DB_NAME = 'pbdata'
DB_USER = 'root'
DB_PASS = ''

def connectMysql():
    print("trying connection to :", DB_NAME)
    connection = mysql.connector.connect(host=DB_HOST,
                                            database=DB_NAME,
                                            user=DB_USER,
                                            password=DB_PASS)
    return connection

def executor(con, filename, fileloc):
    try:
        if con.is_connected():
            hashed = myHash(filename)
            queryStr = myInsertQuery(hashed, filename, fileloc)
            cursor = con.cursor()
            cursor.execute(queryStr)
            con.commit()
            if cursor.rowcount > 0:
                print("-> success insert!")
            else:
                print("-> hash already exist")
                selectQuery = mySelectByHashed(hashed)
                cursor.execute(selectQuery)
                record = cursor.fetchone()
                print("-> hash name = ", record[0])
                print("-> file name = ", record[1])
                print("-> file loc = ", record[2])
                print("-> insert date  = ", record[3])

            cursor.close()
        else:
            print("failed, not connected to db")
    except Exception as e:
        print("-> failed execute query : {}".format(e))

def myHash(str):
    hash_object = hashlib.sha256(str.encode('utf-8'))
    hashed = hash_object.hexdigest()
    # print("str: {}, hash: {}".format(str, hashed))
    return hashed

def mySelectByHashed(hashed):
    queryStr = """SELECT hashname, name, current_path, register_date FROM videos WHERE hashname = '%s'""" % hashed
    return queryStr

def myInsertQuery(hashed, filename, fileloc):
    queryStr = """INSERT INTO videos(hashname, name, current_path)
                    SELECT * FROM (
                        SELECT '%s', 
                            %s, 
                            %s) AS tmp 
                    WHERE NOT EXISTS (
                        SELECT hashname 
                        FROM videos 
                        WHERE hashname = '%s' 
                    ) LIMIT 1""" % (hashed, filename, fileloc, hashed)
    return queryStr

def registerFileName(dir, pattern):
    connection = connectMysql()
    filecount = 0
    for pathAndFilename in glob.iglob(os.path.join(os.getcwd(), pattern)):
        filename, ext = os.path.splitext(os.path.basename(pathAndFilename))
        realname = filename.split("(1)")
        filecount += 1
        name = repr(realname[0])
        path = repr(os.getcwd())
        print("processing file ({}) : {} ({})".format(ext, name, path))
        executor(connection, name, path)
        print(" ")

    if(connection.is_connected()):
        connection.close()

    print("***************** FILE COUNT :", filecount)

if __name__ == '__main__':
    registerFileName(r'./', FILE_FORMAT)
