Project: Microblog Microservices
Author: Brandon Le
Email: le.brandon350@gmail.com


***Getting started***

$ make                           #initializes and populates database
$ foreman start                  #starts services

***API Implementations***

API to view all users
curl http://127.0.0.1:5100/users 

API to create a new user
curl -d '{"username":"Brandon5", "password":"password5", "email":"brandon5@gmail.com"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/create

API to authenticate user information
curl -d '{"username":"Brandon1", "password":"password1"}' -H "Content-Type: application/json" -X GET http://127.0.0.1:5100/auth

API to view all User Followers
curl http://127.0.0.1:5100/userfollows/Brandon2

API to follow a user
curl -d '{"follower":"Brandon4", "followed":"Brandon3"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/addfollower

API to unfollow a user
curl -d '{"username":"Brandon2", "followed":"Brandon1"}' -H "Content-Type: application/json" -X DELETE http://127.0.0.1:5100/removefollower

API to view user timeline
curl http://127.0.0.1:5000/timeline/Brandon1

API to view all user's following timeline
curl http://127.0.0.1:5000/timeline/all

API to post tweet
curl -d '{"username":"Brandon4",  "text":"Hello World"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/timeline/post
