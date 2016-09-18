# -*- coding: utf-8 -*-
import asyncio
from torndb import Connection
from motor.motor_asyncio import AsyncIOMotorClient

ms_db = Connection(host='', database='', 
                user='', password='KY8oyP5fvWMIeMZz4te6')
client = AsyncIOMotorClient('mongodb://192.168.10.204:27017')
mg_db = client['db_php_bsdb']

table_to_coll = {
    't_zone' : 'cs_5754e2118448ea7db4567',
    't_education_level': 'cs_5754e4ef88eae30e8b4567', 
    't_course': 'cs_5754e7f08448e8b4568', 
    't_institution': 'cs_5754ed8a8eaa92f8b457a', 
    't_cs_cases': 'cs_5775ce894eb138b4567', 
    't_cs_students': 'cs_5775c5ae894eb13a638b4567',
    't_course_category': 'cs_5775894eb14f638b4568', 
    't_rank_list': 'cs_5775c5d5894638b4567', 
    't_rank': 'cs_5775c5e589e098b4567' 
}


class ExecQueryError(Exception):
    pass


class EncodeError(Exception):
    pass


def clean_row(row=None):
    c_row = dict()
    for key in row.keys():
        if key.startswith('f_'):
            c_row[key] = row[key]
    return c_row


@asyncio.coroutine
def get_mysql_data(coll_name=''):
    """Return all rows and field starts with `f_`"""
    sql = 'SELECT * FROM `xiongyang`.`{}` ORDER BY id ASC'.format(coll_name)
    try:
        rows = ms_db.query(sql)
    except ExecQueryError as e:
        raise e
    results = list()
    for row in rows:
        c_row = dict()
        for key in row.keys():
            if key.startswith('tmp_'):
                # print(key)
                continue
            c_row[key] = row[key]

        keys = c_row.keys()
        if 'f_birthday' in keys:
            try:
                c_row['f_birthday'] = c_row['f_birthday'].strftime('%Y-%m-%d')
            except:
                c_row['f_birthday'] = ''

            # update = c_row['update'].strftime('%Y-%m-%d')
            # c_row['update'] = str(update)
        if 'f_app_date' in keys:
            try:
                c_row['f_app_date'] = c_row['f_app_date'].strftime('%Y-%m-%d')
            except:
                c_row['f_app_date'] = ''
        if 'f_admitted_date' in keys:
            try:
                c_row['f_admitted_date'] = c_row['f_admitted_date'].strftime('%Y-%m-%d')
            except:
                c_row['f_admitted_date'] = ''
            # update = c_row['f_birthday'].strftime('%Y-%m-%d')
            # c_row['f_birthday'] = str(update)

        # if 'f_id' in keys:
        #     c_row['id'] = c_row.get('f_id')
        #     del c_row['f_id']
        # if 'f_pid' in keys:
        #     c_row['pid'] = c_row.get('f_pid')
        #     del c_row['f_pid']
        # if 'f_status' in keys:
        #     c_row['status'] = c_row.get('f_status')
        #     del c_row['f_status']
        # if 'f_state' in keys:
        #     c_row['status'] = c_row.get('f_state')
        #     del c_row['f_state']

        results.append(c_row)

    return results


@asyncio.coroutine
def do_insert(rows):
    """Insert and opt. test demo."""
    if not rows:
        print('rows error.')
        raise ValueError

    result = yield from mg_db.t_institution.insert(rows)
    print('result {}'.format(result))
    print(len(result))

    cursor = mg_db.t_institution.find({'f_ename': 'Toronto Catholic District School Board'})
    while (yield from cursor.fetch_next):
        doc = cursor.next_object()
        print(doc)


@asyncio.coroutine
def mongo_update_many(coll_name=''):
    """As function name."""
    yield from collection_back(coll_name)
    coll = mg_db[coll_name]
    yield from coll.remove()
    results = yield from get_mysql_data()
    yield from coll.insert(results)


@asyncio.coroutine
def mongo_update_some(name='t_institution', ids=[1, ]):
    """:params-ids :mysql table`s f_id list"""
    if (not ids) and (not isinstance(ids, list)):
        raise ValueError
    coll = mg_db[name]
    sql = 'SELECT * FROM `xiongyang`.`t_institution` WHERE `id` = {}'
    # rows = yield from get_mysql_data(sql, ids)
    for id in ids:
        row = ms_db.get(sql.format(id))
        # print(row.get('f_area_id'))
        doc = yield from coll.find_one({'id': row.get('id')})
        if not doc:
            print(row)
            print('update failed.')
            continue
        c_row = clean_row(row)
        # print(c_row)
        _id = doc['_id']
        print(_id)
        update_doc = yield from coll.update({'_id': _id}, c_row)
    # rows = ms_db.query(sql, ids)
    # print(rows)


@asyncio.coroutine
def collection_back(coll_name=''):
    """Back given collection."""
    if not coll_name:
        print('Args name must.')
        return
    # Get target collection data with list.
    coll = mg_db[coll_name]
    count = yield from coll.count()
    cursor = coll.find({})
    rows = yield from cursor.to_list(length=count)
    print('Target collection has {} document.'.format(count))

    # Back target collection.
    coll_back_name = coll_name + '_back'
    coll_back = mg_db[coll_back_name]
    back_count = yield from coll_back.count()
    if 0 != back_count:
        yield from coll_back.remove()
    yield from coll_back.insert(rows)
    # print(back_result)
    print('Back target collection {} document'.format((yield from coll_back.count())))


@asyncio.coroutine
def mongodb_insert_one(coll_name='', data={}):
    if not data:
        return
    if isinstance(data, dict):
        result = yield from mg_db[coll_name].insert(data)
        print('result {}'.format(result))
    elif isinstance(data, list):
        result = yield from mg_db[coll_name].insert(data)
        print('result {}'.format(result))
        print('Insert {} rows.'.format(len(result)))
    else:
        print('value error.')
        raise ValueError


@asyncio.coroutine
def mongodb_insert_many(coll_name='', data=[]):
    yield from mongodb_insert_one(coll_name, data)


@asyncio.coroutine
def find_all():
    coll = mg_db['t_institution']
    cursor = coll.find({})
    while (yield from cursor.fetch_next):
        doc = cursor.next_object()
        print(doc)


@asyncio.coroutine
def sync_db():
    for key in table_to_coll.keys():
        print(key)
        mg_coll_name = table_to_coll.get(key, '')
        print(mg_coll_name)
        if not mg_coll_name:
            print('Check table to coll maps')
            continue
        results = yield from get_mysql_data(key)
        yield from mongodb_insert_many(mg_coll_name, results)

@asyncio.coroutine
def main():
    yield from sync_db()
    # t_institution
    # t_zone
    # t_education_level
    # t_course
    # 案例 5775c4b8894eb151638b4567 t_cs_cases
    # 学生 5775d818894eb14f638b4569 t_cs_students

    # coll_name = 't_course_category'
    # mg_coll_name = table_to_coll.get(coll_name, '')
    # if not mg_coll_name:
    #     print('Check table to coll maps')
    #     return
    # table_name = 't_cs_students'
    # coll_name = '5775d818894eb14f638b4569'
    # results = yield from get_mysql_data(coll_name)
    # for row in results:
    #     print(row)
    # print('-' * 255)
    # yield from do_insert(results)
    # print('test insert one row.')
    # yield from mongodb_insert_one(results[0])
    # print('test insert many row.')
    # yield from mongodb_insert_many(coll_name, results)
    # yield from mongodb_insert_many(mg_coll_name, results)
    # yield from mg_db.t_institution.remove()
    # yield from collection_back('t_institution')
    # yield from mongo_update_many('t_institution')
    # yield from mongo_update_some()
    # yield from find_all()

if __name__ == '__main__':
    print('running ... ')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


