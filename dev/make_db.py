from snappy import *
import os
import sqlite3
import binascii

snappy_schema = """
CREATE TABLE census (
 id integer primary key,
 name text,
 volume real,
 chernsimons real,
 triangulation blob)
"""

insert_query = """insert into census
(name, volume, chernsimons, triangulation)
values ('%s', %s, %s, X'%s')"""

def create_census(connection):
    connection.execute(snappy_schema)
    connection.commit()
    
def insert_manifold(connection, mfld):
    name = mfld.name()
    volume = mfld.volume()
    try:
        cs = mfld.chern_simons()
    except:
        cs = 'NULL'
    triangulation = binascii.hexlify(mfld._to_bytes())
    query = insert_query%(name, volume, cs, triangulation)
    try:
        connection.execute(query)
    except:
        print query

def main():
    if os.path.exists('census.sqlite'):
        print '%s already exists!'%'census.sqlite'
    snappy_connection = sqlite3.connect('census.sqlite')
    create_census(snappy_connection)
    for M in OrientableCuspedCensus():
        insert_manifold(snappy_connection, M)
    snappy_connection.commit()
if __name__ == '__main__':
    main()
