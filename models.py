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
    with open(path, "rb") as f:
        binary_string = base64.b64encode(f.read()).decode('utf-8')      
    return binary_string

with open("image_api/credentials.json") as f:
    creds = json.load(f)

user, pwd = creds['mysql']['user'], creds['mysql']['pwd']
engine = create_engine(f"mysql+pymysql://{user}:{pwd}@db/Pictures")
  
   
def tags(path, tags):
    with engine.connect() as con:
        con.execute(f"""INSERT INTO pictures (path, date)
            VALUES ('{path}','{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            """)
    
    with engine.connect() as con:
        det = con.execute(f"""SELECT id, date 
                            FROM pictures WHERE path = '{path}'""").fetchall()
    
    id, date = det[0][0], det[0][1]
    
    data = [
        (
            t['tag'],
            t['conf'],
        )
        for t in tags
    ]
    
    with engine.connect() as con:
        for (tag, conf) in data:
            con.execute(f"INSERT INTO tags VALUES('{tag}',{id},{conf},'{date}')")
    
    return {
        "id": id,
        "size": get_size(path),
        "date": date,
        "tags": tags
    }


def get_image(id):
    with engine.connect() as con:
        data = con.execute(f"""SELECT P.id, P.date, T.tag, T.confidence
                                FROM pictures AS P 
                                INNER JOIN tags AS T ON P.id = T.picture_id
                                WHERE id = {id}""").fetchall()
        
    with engine.connect() as con:
        path = con.execute(f"SELECT path FROM pictures WHERE id = {id}").fetchall()
    
    result = [dict((key, value) for key, value in row.items()) for row in data]
    
    result.append({'size': get_size(path[0][0])})
    result.append({'data': get_data(path[0][0])})
    
    return result


def get_images(min_date, max_date, tags):
    sql_select = """SELECT P.id, P.date, T.tag, T.confidence
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
        data = con.execute(sql_select + sql_where).fetchall()
    
    return [dict((key, value) for key, value in row.items()) for row in data]


def get_tags(min_date, max_date):   
    sql_select = """SELECT tag, 
                        COUNT(DISTINCT picture_id) as n_images,
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
        data = con.execute(sql_select + sql_where + sql_groupby).fetchall()
    
    return [dict((key, value) for key, value in row.items()) for row in data]