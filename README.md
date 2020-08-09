# Sound Registry Service

## Usage

* POST raw audio data and store it.

    * Eg: $ curl -X POST --data-binary @myfile.wav http://localhost/post

* GET a list of stored files, GET the content of stored files, and GET metadata of
stored files, such as the duration of the audio. The GET endpoint(s) should
accept a query parameter that allows the user to filter results. Results should be
returned as JSON.
    * Eg: $ curl http://localhost/download?name=myfile.wav -o <filename\>
    * Eg: $ curl http://localhost/list?maxduration=300
    * Eg: $ curl http://localhost/info?name=myfile.wav

## Example commands

### Register sounds
* curl -X POST --data-binary @myfile.wav http://localhost/post
* curl -X POST --data-binary @bokunofairu.wav http://localhost/post
* curl -X POST --data-binary @meuarquivo.wav http://localhost/post

### Gather info
* curl http://localhost/info?name=bokunofairu.wav
* curl http://localhost/info?name=meuarquivo.wav
* curl http://localhost/info?name=myfile.wav

### Download sounds
* curl http://localhost/download?name=myfile.wav -o test.wav
* curl http://localhost/download?name=myfile.wav -o -

### List sounds
* curl http://localhost/list?name=meuarquivo.wav\&maxduration=4
* curl http://localhost/list?name=meuarquivo.wav\&maxduration=2.7
* curl http://localhost/list?name=meuarquivo.wav\&maxduration=2.6
* curl http://localhost/list?name=meuarquivo.wav\&maxduration=2.52
* curl http://localhost/list?name=meuarquivo.wav\&maxduration=2.53
* curl http://localhost/list?name=myfile.wav\&maxduration=3
* curl http://localhost/list?name=myfile.wav\&maxduration=3
* curl http://localhost/list?name=myfile.wav\&maxduration=4

### Adding the superuser (first user)
* curl -v -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"superpwd"}' http://localhost/users

### Adding admin user (only via superuser)
* curl -v -X POST -H "Content-Type: application/json" -d '{"username":"admin2","password":"admin2", "type": "1", "auth": "superpwd"}' http://localhost/users

### Update superuser
* curl -v -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin", "auth": "superpwd"}' http://localhost/users

### Normal user sign up
* curl -v -X POST -H "Content-Type: application/json" -d '{"username":"oper","password":"oper"}' http://localhost/users

### Update normal user sign up
* curl -v -X POST -H "Content-Type: application/json" -d '{"username":"oper","password":"oper", "auth": "oper"}' http://localhost/users


* curl http://localhost/list?name=meuarquivo.wav\&maxduration=4 --user admin:admin


* curl http://localhost/authtest
* curl http://localhost/authtest --user admin:pwd
* curl http://localhost/authtest --user admin:superpwd
* curl http://localhost/authdownload?name=myfile.wav
* curl http://localhost/authdownload?name=myfile.wav --user admin:pwd
* curl http://localhost/authdownload?name=myfile.wav --user admin:superpwd
* curl http://localhost/authlist
* curl http://localhost/authlist --user admin:pwd
* curl http://localhost/authlist --user admin:superpwd
* curl http://localhost/authdownload?name=myfile.wav
* curl http://localhost/authdownload?name=myfile.wav
* curl --user admin:superpwd http://localhost/authdownload?name=myfile.wav
 


## Sources

* https://docs.faculty.ai/user-guide/apis/flask_apis/flask_file_upload_download.html
* https://flask-restful.readthedocs.io/en/latest/reqparse.html
* https://github.com/jakewright/tutorials/tree/master/home-automation/02-device-registry
* https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
* https://realpython.com/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/
* https://www.geeksforgeeks.org/retrieving-and-updating-data-contained-in-shelve-in-python/
* https://realpython.com/introduction-to-flask-part-2-creating-a-login-page/
* https://realpython.com/using-flask-login-for-user-management-with-flask/
* https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-online-version-spring-2019/implementing-rest-apis-with-flask/
* https://stackoverflow.com/questions/39834436/flask-restful-app-fails-when-authentication-is-enabled

https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx
https://stackoverflow.com/questions/58271312/run-flask-application-with-nginx-and-https
https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a