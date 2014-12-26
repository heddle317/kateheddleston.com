kateheddleston.com
==================

My personal website. It's a janky little thing :) I spent entirely too much time building this. This website is built with python, flask, sqlalchemy, and narcissism.


Design inspiration
------------------
* computer engineering barbie
* http://yaronschoen.com/info/ (although not the pink, the pink comes from computer engineering barbie)
* https://medium.com
* This blog post on best fonts for reading: http://www.huffingtonpost.com/2014/07/28/font-ranking_n_5625650.html


Recommended Tutorials for building an app like this:
---------------------------------------------------
* Flask MegaTutorial - http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
* learnpythonthehardway - http://learnpythonthehardway.org/
* fullstackpython - http://www.fullstackpython.com/


How to setup this code repository if you want to fork it and use it for your own nefarious purposes:
---------------------------------------------------------------
* To setup the app locally:
  * Get setup with ```mkvirtualenv`` - http://newcoder.io/pyladiessf/
  * ```mkvirtualenv [venv-name]```
  * ```pip install -r requirements.txt```
  * Create a keys.sh file locally. This will hold all the keys you need for interfacing with Facebook, Twitter, AWS, PostmarkApp, etc (see below for the full list of third party accounts and environment variables needed).
  * Create the Database
    * Install PostgresApp locally
    * ```CREATE DATABASE [database name]```
    * ```./run.sh ./scripts/run_migrations.py```
  * Add an admin user to the database:
    * ```./run.sh ./scripts/add_user.py '[email]' '[password]'```
* To run the app locally:
  * ```./run.sh web.py```
* To deploy to Heroku:
  * Follow the instructions for creating a heroku account, installing the toolbelt, and creating a heroku app here (but you don't need to write the app code or Procfile since that's already in this repo): https://devcenter.heroku.com/articles/getting-started-with-python#introduction
  * ```heroku config:set BUILDPACK_URL='git://github.com/kennethjiang/heroku-buildpack-python-libffi.git'```
  * ```heroku config:set ENVIRONMENT='production'```
  * Configuring custom domains with heroku:
    * https://devcenter.heroku.com/articles/custom-domains
  * Setting up SSL with heroku (this is the only thing that costs money)
    * https://devcenter.heroku.com/articles/ssl-endpoint
    * https://devcenter.heroku.com/articles/ssl-certificate-dnsimple


Environment Variables and Third Party Apps
------------------------------------------
Here's the full list of third party accounts and environment variables you'll need. You'll need to add these via ```heroku config:set VARIABLE_NAME='[value]'``` and to the key.sh file you have locally (```export VARIABLE_NAME='[value]'```).
* AWS
  * AWS_ACCESS_KEY_ID
  * AWS_SECRET_ACCESS_KEY
  * AWS_IMAGE_BUCKET (you create this bucket once you've created your aws account)
  * AWS_STATIC_BUCKET (same as image bucket)
* Bugsnag
  * BUGSNAG_KEY
* Facebook
  * FACEBOOK_APP_ID
  * FACEBOOK_APP_SECRET
* Flask
  * FLASK_SECRET_KEY (e.g. '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13', but create your own hash)
  * FLASK_MODEL_HASH (create the same way as the FLASK_SECRET_KEY, but should not be the same)
* Logentries
  * LOGENTRIES_TOKEN
* PostmarkApp
  * POSTMARKAPP_API_KEY
* Twitter
  * TWITTER_CONSUMER_KEY
  * TWITTER_CONSUMER_SECRET

 
Tools used
----------------------------
* fullpage.js - http://alvarotrigo.com/fullPage/
* masonry.js - http://masonry.desandro.com/
* bootstrap - http://getbootstrap.com
* AngularJS - https://angularjs.org/
* Flask - http://flask.pocoo.org/
* SQLAlchemy - http://www.sqlalchemy.org/
* PostgreSQL - http://www.postgresql.org/
