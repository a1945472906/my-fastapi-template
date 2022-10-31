@@ -0,0 +1,24 @@
# my-fastapi-template 


web template use fastapi,postgres,envoy


Usage
----
install
```sh
pip install -r requirements.txt
```
run postgres && envoy proxy
```sh
docker-compose up -d
```
run serve
```sh
python3 -m uvicorn main:app --port 8080 --reload
```
test server
```sh
curl.exe localhost:8086/user/login -H "Content-Type:application/json" -X POST -d '{\"username\":\"admin\",\"password\":\"password\"}'
```