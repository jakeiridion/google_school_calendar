### **`Description:`**
This App parses the Eltenportal Website's exam timetable and creates a Google calendar
based on the information. It then keeps the calendar updated.

****
### **`Install Requirements:`**
You need to have the following packages installed before running this app.
You will need pip.
* requests: "sudo python3 -m pip install requests"
* bs4 (BeautifulSoup): "sudo python3 -m pip install bs4"
* google api client: "sudo python3 -m pip install google-api-python-client"
* google OAuth library: "sudo python3 -m pip install google_auth_oauthlib"

****
### **`Setting up the app:`**
In order to run this app you have to follow the following steps:
1. Go to "https://console.developers.google.com/" and create a new Project.
2. Select your project and search for the Calendar api.
3. Activate the calendar api for your project.
4. Create OAuth 2.0 credentials by going to the credentials section.
5. Download your client_secret.json file by clicking on the download button
   next to your newly created credentials. (Under OAuth 2.0-Client-IDs)
6. Dump the client_secret.json file in the project's main directory.
7. Open and set up the SETTINGS.ini file.
8. You are all done now, however the first time running the app will be different
   from the other times so look below.
  
****
### **`The first run:`**
When running the app for the first time you will be asked to login with
whatever account you want the calendar to be created on. After that the app
will create a token.pkl file which saves your access token and helps you by not
forcing you to redo the authentication process every single time.
<br> 
Simply type: "python3 main.py" and follow the steps given by the app.
<br>
<br>
After the token.pkl file was created you can exit the app or wait until the
calendar and all the events have been created. To follow the app's process read the log.
After you exit the app you can restart it with the following command, forcing it to run
in the background and allowing you to close the ssh connection without closing the app:
<br>
"sudo nohup python3 main.py &"
<br>
Even tough the app was restarted it will not create a new calendar, because it
saved the calendar-id in the file calendarID.

****
### **`Deleting your calendar:`**
If you want the app to create a completely new calendar and stop updating the
first one just delete the calendarID file located in the dependencies folder and restart the app. 

