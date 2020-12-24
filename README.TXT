Project: Caching
Author: Brandon Le
Email: le.brandon350@gmail.com


***Getting started***

$ make                           #initializes and populates database
$ foreman start                  #starts services

***API Implementations***

API to view user home timeline
curl http://127.0.0.1:5000/timeline/home/Brandon1

API to view all user's following timeline
curl http://127.0.0.1:5000/timeline/all

API to post tweet
curl -d '{"username":"Brandon4",  "text":"Hello World"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/timeline/post

***HTTP Caching: The Public Timeline***
1. $ curl http://127.0.0.1:5000/timeline/all
2. Open web browser to http://127.0.0.1:5000/timeline/all
3. Refresh the page
4. $ curl -d '{"username":"Brandon4",  "text":"5 Minutes Later"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/timeline/post
5. Refresh the page again to see no changes
6. Refresh the page again 5 minutes later to see updated changes

***Object Caching: Home Timelines***
1. $ curl http://127.0.0.1:5000/timeline/home/Brandon1
2. Open browser to http://127.0.0.1:5000/timeline/home/Brandon1
3. Open browser to http://127.0.0.1:5000/timeline/home/Brandon3 to see object loaded from cache