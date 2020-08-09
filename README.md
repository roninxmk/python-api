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

### Authorization test
* curl http://localhost/authtest
* curl http://localhost/authtest --user admin:pwd
* curl http://localhost/authtest --user admin:superpwd

### Download with credentials check
* curl http://localhost/authdownload?name=myfile.wav 
* curl http://localhost/authdownload?name=myfile.wav --user admin:superpwd -o <filename\>
* curl http://localhost/authdownload?name=myfile.wav --user admin:superpwd -o -

### List with credentials check
* curl http://localhost/authlist
* curl http://localhost/authlist --user admin:pwd
* curl http://localhost/authlist?name=myfile.wav\&maxduration=4 --user admin:superpwd
* curl http://localhost/authlist?name=myfile.wav\&maxduration=3 --user admin:superpwd

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
* https://help.parsehub.com/hc/en-us/articles/217751808-API-Tutorial-How-to-get-run-data-using-Python-Flask
* https://www.jameskozlowski.com/index.php/2018/04/14/a-simple-flask-api-example/
* http://zetcode.com/python/flask/

## Future reading

* https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx
* https://stackoverflow.com/questions/58271312/run-flask-application-with-nginx-and-https
* https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04
* https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a
* https://nearsoft.com/blog/how-to-create-an-api-and-web-applications-with-flask/
* https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
* https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html

# Benchmarks

* From 2012: https://blog.kgriffs.com/2012/12/18/uwsgi-vs-gunicorn-vs-node-benchmarks.html
* From 2017: https://www.toptal.com/back-end/server-side-io-performance-node-php-java-go
* From 2020: https://www.mindinventory.com/blog/python-vs-node-js/

# Usage from local machine

Inside the python-api folder:
 
* sudo docker-compose up --build