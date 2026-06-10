import httpx
import redis
import pymongo
    
def test_app_is_running():
    try:
        response = httpx.get("http://localhost:8000/docs")
        assert response.status_code == 200
    except Exception as e:
        assert False, f"App is not running: {e}"

def test_cache_is_running():
    try:
        client = redis.Redis(host="localhost", port=6379)
        assert client.ping() == True
    except Exception as e:
        assert False, f"Cache is not running: {e}"

def test_database_is_running():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        client.admin.command('ping')
    except Exception as e:
        assert False, f"Database is not running: {e}"