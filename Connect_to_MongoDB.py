import re
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


async def ping_server():
    uri = "mongodb://localhost:27017/"
    client = AsyncIOMotorClient(uri)

    try:
        client.admin.command('ping')
        print("Successfully connected to database")
        return True, client
    except Exception as e:
        print(e)
        return False, None


async def connect_to_database(client, db_name):
    database_list = await client.list_database_names()
    if db_name in database_list:
        my_db = client[db_name]
        return my_db
    else:
        my_db = client[db_name]
        return my_db


async def connect_to_collection(my_db, collection_name):
    collection_list = await my_db.list_collection_names()
    if collection_name in collection_list:
        my_collection = my_db[collection_name]
        return my_collection
    else:
        my_collection = my_db[collection_name]
        return my_collection


async def add_to_collection(my_collection, data):
    if type(data) is dict:
        await my_collection.insert_one(data)
    elif type(data) is list:
        await my_collection.insert_many(data)


async def read_from_collection(my_collection):

    async for x in my_collection.find():
        print(x)


async def connection(database_name, collection_name):
    global collection_status, my_collection
    ping_status, client = await ping_server()
    if ping_status:
        my_db = await connect_to_database(client, database_name)
        my_collection = await connect_to_collection(my_db, collection_name)
        return client, my_collection


def extract_object_id(id_string):
    match = re.search(r"ObjectId\('(.+)'\)", id_string)
    if match:
        object_id_str = match.group(1)
        return ObjectId(object_id_str)
    return None


async def main(team_title, decrease):
    global members
    client, users_collection = await connection('GoharPazhohan', 'Users')
    client, teams_collection = await connection('GoharPazhohan', 'Teams')

    teams_with_members = []

    async for team in teams_collection.find({'Title': team_title}):
        members = []
        for member_id in team["Members"]:
            member_id = extract_object_id(member_id)
            member = await users_collection.find_one({"_id": member_id})
            if member:
                members.append({"name": member["name"], "age": member["age"]})

    members_sorted = sorted(members, key=lambda x: x["age"], reverse=decrease)
    teams_with_members.append({"title": team_title, "members": members_sorted})

    client.close()
    json_string = json.dumps(teams_with_members)
    json_info = json.loads(json_string)
    return json_info
