#CSC 315 Final 2023
#Fabio Pecora
import mysql.connector
from pprint import pprint
import sys

# connect to db as user the user api and input the password

    db  = mysql.connector.connect(
        host='localhost',
        user='api',
        password='GRAPH123',
        database='CSC315Final2023'
    )
    print("Error: Cannot connect to the database.")
    sys.exit(1)

mycursor = mydb.cursor()
mydb.commit()

def getError(error, result):
    return (error, result)

def queryExecute(query, *args):
    try:
        cursor.execute(query % (args))
    except mysql.connector.Error as err:
        return getError(True, err)

    return getError(False, [*mycursor])


# insert  new users into the database

def NewUser(userID, name, country):
    query = 'INSERT INTO User VALUES (%s, \'%s\', \'%s\');'
    return queryExecute(query, userID, name, country)

# insert  the name and band


# check if the band exists in the database
def addFavorite(userID,bandName):
    _, result = queryExecute('SELECT bname FROM Bands WHERE bname=\'%s\';',bandName)
    bandExists = len(result) > 0

    if not bandExists:
        return getError(True, f'Error: {bandName} does not exist. It is most likely not in the database')

    _, bandID = queryExecute('SELECT bid FROM Bands WHERE bname=\'%s\';',bandName)
    bandID = bandID[0][0]

    query = 'INSERT INTO Favorites values (%s, %s);'
    return queryExecute(query, userID, bandID)


def deleteFavorite(userID,bandName):
    _, result = queryExecute('SELECT bname FROM Bands WHERE bname=\'%s\';',bandName)
    bandExists = len(result) > 0

    if not bandExists:
        return getError(True, f'Error: {bandName} does not exist. It is most likely not in the database.')

    _, bandID = queryExecute('SELECT bid FROM Bands WHERE bname=\'%s\';',bandName)
    bandID = bandID[0][0]

    query = 'DELETE FROM Favorites WHERE uid=%s AND bid=%s;'
    return queryExecute(query, userID, bandID)




# insert to users to the databse
newUser(1,'Fabio Pecora', 'United States')
newUser(2,'Marco Mengoni', 'Italy')
newUser(3,'Francesco Pecora', 'United States')
newUser(4,'Cristiano Ronaldo', 'Portugal')
newUser(5,'Lebron James', 'United States')
newUser(4,'Lionel Messi', 'Argentina')

pprint(queryExecute('SELECT * FROM User;'))

# inserting  favorites to the database
addFavorite(1, 'Seputura')
addFavorite(1, 'Led Zeppelin')
addFavorite(1, 'Twisted Sister')
addFavorite(1, 'Sade')

addFavorite(2, 'The Guess Who')
addFavorite(2, 'Mozart')
addFavorite(2, 'Seputura')
addFavorite(2, 'Led Zeppelin')

addFavorite(3, 'Sade')
addFavorite(3, 'Mozart')
addFavorite(3, 'Twisted Sister')
addFavorite(3, 'Led Zeppelin')

addFavorite(4, 'Mozart')
addFavorite(4, 'The Hu')
addFavorite(4, 'Paul Pena')
addFavorite(4, 'Led Zeppelin')

addFavorite(5, 'Tengger Cavalry')
addFavorite(5, 'Paul Pena')
addFavorite(5, 'Sade')
addFavorite(5, 'Battuvshin')

addFavorite(6, 'Tengger Cavalry')
addFavorite(6, 'The Hu')
addFavorite(6, 'Sade')
addFavorite(6, 'Battuvshin')

pprint(queryExecute('SELECT * FROM Favorites;'))


# creating query to show which subgenres come from which regions
def getSubGenreRegion():
    query = '''SELECT DISTINCT S.sgname, R.rname FROM Band_Styles S JOIN
    (SELECT O.bname, C.rname FROM Band_Origins O JOIN Country C
        WHERE C.cname = O.cname
    ) AS R
    WHERE S.bname = R.bname;'''
    return queryExecute(query)


# other bands as those in favorites
def otherBands(userID):
    query = '''SELECT bname FROM
    (SELECT DISTINCT sgname FROM
        (SELECT bname FROM Bands WHERE bid IN
            (SELECT bid FROM Favorites WHERE uid=%s)
        ) as InFavorites
        JOIN
        (SELECT bname,sgname FROM Band_Styles) as Styles
        WHERE UserFavorites.bname=Styles.bname) AS SGUserFavorites
    JOIN
    (SELECT DISTINCT NotFavorites.bname,sgname FROM
        (SELECT bid,bname FROM Bands WHERE bid NOT IN
            (SELECT bid FROM Favorites WHERE uid=%s)
        ) as NotFavorites
        JOIN
        (SELECT bname,sgname FROM Band_Styles) as Styles
        WHERE NotFavorites.bname=Styles.bname) AS SGNotUserFavorites
    WHERE SGNotUserFavorites.sgname=SGUserFavorites.sgname;'''
    return queryExecute(query,userID, userID)

# bands not in favorite that are the same genre
def BandsByGenre(userID):
    query = '''SELECT DISTINCT GNotUserFavorites.bname FROM

        (SELECT DISTINCT UserFavorites.bname,BGenre.gname FROM
            (SELECT bname FROM Bands WHERE bid IN
                (SELECT bid FROM Favorites WHERE uid=%s)
            ) as UserFavorites
            JOIN
            (SELECT Style.bname,Style.sgname,SGenre.gname FROM
                Band_Styles Style JOIN Sub_Genre SGenre
                    where Style.sgname=SGenre.sgname
                ) AS BGenre
        WHERE UserFavorites.bname=BGenre.bname) AS GUserFavorites

        JOIN

        (SELECT DISTINCT NotUserFavorites.bname,BGenre.gname FROM
            (SELECT bname FROM Bands WHERE bid NOT IN
                (SELECT bid FROM Favorites WHERE uid=%s)
            ) as NotUserFavorites
            JOIN
            (SELECT Style.bname,Style.sgname,SGenre.gname FROM
                Band_Styles Style JOIN Sub_Genre SGenre
                    where Style.sgname=SGenre.sgname
                ) AS BGenre
        WHERE NotUserFavorites.bname=BGenre.bname) AS GNotUserFavorites

    WHERE GNotUserFavorites.gname=GUserFavorites.gname;'''
    return queryExecute(query,userID, userID)

# users with the same favorites
def OtherUsers(userID):
    query = '''SELECT bname FROM Bands JOIN
        (SELECT DISTINCT bid FROM
            (SELECT uid FROM Favorites WHERE bid IN
                (SELECT bid FROM Favorites WHERE uid=%s)
                    AND uid!=%s) AS OtherUsers
            JOIN
            (select * from Favorites) AS F
        WHERE F.uid=OtherUsers.uid) AS OtherFavorites
    WHERE Bands.bid=OtherFavorites.bid;'''
    return queryExecute(query, userID, userID)


# countries of bands the user liked
def countriesByGenre(userID):
    query = '''SELECT DISTINCT cname FROM Band_Origins
    JOIN
        (SELECT DISTINCT BGenre.* FROM
            (SELECT bname FROM Bands WHERE bid IN
                (SELECT bid FROM Favorites WHERE uid=%s)
            ) as UserFavorites
            JOIN
            (SELECT Style.bname,Style.sgname,SGenre.gname FROM
                Band_Styles Style JOIN Sub_Genre SGenre
                    where Style.sgname=SGenre.sgname
                ) AS BGenre
        WHERE InFavorites.bname=BGenre.bname) AS UserGenres
    WHERE Band_Origins.bname=UserGenres.bname AND
    cname NOT IN (SELECT homeCountry FROM User WHERE uid=%s);'''
    return queryExecute(query, userID, userID)

if __name__ == '__main__':
    db.commit()
    db.close()
    print('Successfully closed connection and changes have been saved.')
else:
    print('something went wrong, changes were not saved)

