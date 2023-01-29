from datetime import datetime
from sqlalchemy import create_engine
import base64
import io
import json
import pymysql

def get_size(path):
    with open(path, "r") as f:
        pos = f.tell()
        f.seek(0, io.SEEK_END)
        size = f.tell()
    return size

def get_data(path):
    with open(path, "r") as f:
        binary_image = base64.b64decode(f)      
    return binary_image

with open("credentials.json") as f:
    creds = json.load(f)

user, pwd = creds['mysql']['user'], creds['mysql']['pwd']
engine = create_engine(f"mysql+pymysql:/{user}:{pwd}@localhost/Pictures")
  
   
def tags(path, tags):
    with engine.connect() as con:
        result = con.execute(f"""INSERT INTO pictures (path, date)
            VALUES ('{path}','{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            """)
    
    with engine.connect() as con:
        det = con.execute(f"SELECT id, date FROM pictures WHERE path = '{path}'")
    
    data = [
        (
            t['tag'],
            i['id'],
            t['conf'],
            i['date'],
        )
        for i in det
        for t in tags
    ]
    
    with engine.connect() as con:
        for (tag, id, conf, date) in data:
            con.execute(f"INSERT INTO tags VALUES('{tag}',{id},{conf},'{date}')")
    
    return {
        "id": det['id'],
        "size": get_size(path),
        "date": det['date'],
        "tags": tags
    }


def get_images(min_date, max_date, tags):
    sql_select = """SELECT P.id, p.size, P.date, T.tag,
                        T.condifence
                    FROM pictures AS P 
                    INNER JOIN tags AS T ON P.id = T.picture_id """
    
    sql_where = ""
    if min_date is not None and max_date is not None:
        sql_where = f"WHERE date >= '{min_date}' AND date <= '{max_date}'"
    elif min_date is not None:
        sql_where = f"WHERE date >= '{min_date}'"
    elif max_date is not None:
        sql_where = f"WHERE date <= '{max_date}'"
    else:    
        sql_where
        
    if tags is not None and len(sql_where) > 0:
        sql_where += f" AND T.tag IN ({tags})"
    elif tags is not None:
        sql_where = f"WHERE T.tag IN ({tags})"""

    with engine.connect() as con:
        result = con.execute(sql_select + sql_where)
    
    return result


def get_image(id):
    with engine.connect() as con:
        result = con.execute(f"""SELECT P.id, p.size, P.date, T.tag,
                                    T.condifence
                                FROM pictures AS P 
                                INNER JOIN tags AS T ON P.id = T.picture_id
                                WHERE id = '{id}'""")
        
    with engine.connect() as con:
        path = con.execute(f"SELECT path FROM pictures WHERE id = '{id}'")
    
    result += get_data(path)
    
    return result


def get_tags(min_date, max_date):   
    sql_select = """SELECT tag, 
                        COUNT(DISTINCT id) as n_images,
                        MIN(confidence) as min_confidence,
                        MAX(confidence) as max_confidence,
                        AVG(confidence) as mean_confidence
                        FROM tags """
    
    sql_groupby = " GROUP BY tag"
    
    sql_where = ""
    if min_date is not None and max_date is not None:
        sql_where = f"WHERE date >= '{min_date}' AND date <= '{max_date}'"
    elif min_date is not None:
        sql_where = f"WHERE date >= '{min_date}'"
    elif max_date is not None:
        sql_where = f"WHERE date <= '{max_date}'"
    else:    
        sql_where
        
    with engine.connect() as con:
        result = con.execute(sql_select + sql_where + sql_groupby)
    
    return result