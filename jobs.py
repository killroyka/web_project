from requests import get, post, delete, put
from pprint import pprint

pprint(get('http://localhost:5001/api/fun').json())