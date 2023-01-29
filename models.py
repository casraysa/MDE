from datetime import datetime
from sqlalchemy import create_engine
import json
import pymysql

with open("credentials.json") as f:
    creds = json.load(f)

user, pwd = creds['mysql']['user'], creds['mysql']['pwd']
engine = create_engine(f"mysql+pymysql:/{user}:{pwd}@localhost/Pictures")

    
def add_photo(path, size, imgstr):
    date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with engine.connect() as conn:
        conn.execute(f"""INSERT INTO pictures (path, date) 
                        VALUES ('{path}','{date}','{size}','{imgstr}')""")


def get_photo_dict(path):
    with engine.connect() as conn:
        result = conn.execute(f"""SELECT id, date 
                                FROM pictures WHERE path = '{path}'""")
    return [{column: value for column, value in row.items()} for row in result]

   
def insert_tags(photo_dict, tags):
    data = [
        (
            t['tag'],
            i['id'],
            t['conf'],
            i['date'],
        )
        for i in photo_dict 
        for t in tags
    ]
    
    with engine.connect() as conn:
        for (tag, id, conf, date) in data:
            conn.execute(f"""INSERT INTO tags 
                            VALUES ('{tag}',{id},{conf},'{date}')""")            

   
def get_images():
    with engine.connect() as conn:
        result = conn.execute(f"""SELECT P.id, p.size, P.date, T.tag AS tags
                                FROM pictures AS P 
                                INNER JOIN tags AS T ON P.id = T.picture_id""")
    return result


def get_image(id):
    with engine.connect() as conn:
        result = conn.execute(f"""SELECT P.id, p.size, P.date, T.tag,
                                    T.condifence, P.data
                                FROM pictures AS P 
                                INNER JOIN tags AS T ON P.id = T.picture_id
                                WHERE id = '{id}'""")
    return result


def get_tags(min_date, max_date):
    if min_date is not None and max_date is not None:
        with engine.connect() as conn:
            result = conn.execute(f"""SELECT tag, 
                                        COUNT(DISTINCT id) as n_images,
                                        MIN(confidence) as min_confidence,
                                        MAX(confidence) as max_confidence,
                                        AVG(confidence) as mean_confidence
                                    FROM tags
                                    WHERE date >= '{min_date}'
                                    AND date <= '{max_date}'
                                    GROUP BY tag""")
    elif min_date is not None:
        with engine.connect() as conn:
            result = conn.execute(f"""SELECT tag, 
                                        COUNT(DISTINCT id) as n_images,
                                        MIN(confidence) as min_confidence,
                                        MAX(confidence) as max_confidence,
                                        AVG(confidence) as mean_confidence
                                    FROM tags
                                    WHERE date >= '{min_date}'
                                    GROUP BY tag""")
    else:
        with engine.connect() as conn:
            result = conn.execute(f"""SELECT tag,
                                        COUNT(DISTINCT id) as n_images,
                                        MIN(confidence) as min_confidence,
                                        MAX(confidence) as max_confidence,
                                        AVG(confidence) as mean_confidence
                                    FROM tags
                                    GROUP BY tag""")
    return result