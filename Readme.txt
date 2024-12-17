This is a master file of all scrapers being built for ecombuddha's internal use. 

For usage, in the terminal, first activate the scraper virtual environment. Ie, use 
scraper\Scripts\activate
to actvate the relavent virtual environment. 

Next Traverse to the scraper you'd like. app for product data(ASIN	Title	Price	Attributes	Bullet Points), but without images and customer reviews. 
(In the virtual env)
cd app
python app.py

This should provide with a live server running on the local host. Look for an o/p response like below. 
 * Serving Flask app 'app'
 * Debug mode: on
2024-12-17 14:13:37,962 - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2024-12-17 14:13:37,963 - INFO - Press CTRL+C to quit
2024-12-17 14:13:37,966 - INFO -  * Restarting with stat
2024-12-17 14:13:39,085 - WARNING -  * Debugger is active!
2024-12-17 14:13:39,091 - INFO -  * Debugger PIN: 777-720-125


From the op, fint the http link, and traverse to it by ctrl+click on the ip. for eg 
 * Running on http://127.0.0.1:5000
is the ip, ctrl+ click on the link above will open the app on the default browser. 