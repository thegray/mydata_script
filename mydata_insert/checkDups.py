import glob, os
import mysql.connector
from mysql.connector import Error
import hashlib

FILE_FORMAT_PATTERN = r'*.mp4'
FILE_FORMAT_TARGET = ".mp4"
DB_HOST = 'localhost'
DB_NAME = 'pbdata'
DB_USER = 'root'
DB_PASS = ''
DIR_EXCLUSION = ["online_course"]

def isDirExcluded(dirname) :
    for excl in DIR_EXCLUSION:
        if excl in dirname:
            return True
    return False

def connectMysql():
    print("trying connection to :", DB_NAME)
    connection = mysql.connector.connect(host=DB_HOST,
                                            database=DB_NAME,
                                            user=DB_USER,
                                            password=DB_PASS)
    return connection

def executor(con, hashed, filename, fileloc):
    try:
        if con.is_connected():
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

def checkDupe(hashToFileLoc, hashed, filename, fileloc):
    if hashed in hashToFileLoc:
        print("-> Dupe: ")
        print("-> file name = ", filename)
        print("-> file loc = ", fileloc)
        print("-> dupe loc = ", hashToFileLoc[hashed])
        print(" ")
        return True
    else:
        hashToFileLoc[hashed] = fileloc
        return False
    return False

def registerFileName(dir, pattern):
    # connection = connectMysql()

    ###################################################

    hashToFileLoc = {}
    dupecount = 0
    cwd = os.getcwd()
    for dirName, _, fileList in os.walk(cwd):
        # print('Found directory: %s' % dirName)
        if not isDirExcluded(dirName):
            for fname in fileList:
                if fname.endswith(FILE_FORMAT_TARGET):
                    filename = fname.split(FILE_FORMAT_TARGET)
                    realname = filename[0].split("(1)")
                    name = repr(realname[0]+ FILE_FORMAT_TARGET)
                    path = repr(dirName)
                    hashed = myHash(name)
                    if checkDupe(hashToFileLoc, hashed, name, path) == True:
                        dupecount += 1

    # if(connection.is_connected()):
    #     connection.close()

    print("***************** DUPE COUNT :", dupecount)

if __name__ == '__main__':
    registerFileName(r'./', FILE_FORMAT_PATTERN)
