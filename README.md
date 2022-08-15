# currency-tracker
Displaying currency exchange rates in an interactive manner

## Note : The details that allow you to connect to your local SQL servers should be modified, as here I've specified the details to my own local SQL server, you will need to change the details to allow the Python code access into your SQL server.

This is a school project, so forgive the long and irrelevant explanations :)

My project is titled "API based Currency Tracker". The project takes real(live) time data regarding the exchange rates of all the currencies by using an API provided by a certain site. It then parses the data and stores it into the SQL database. It then creates graphs based on the recent trends of values and also creates a local page for the display of the output, which is based on what the user has searched for.

As soon as the program is executed, there are API calls made to the website, fixer.io, which contains all the data regarding current and past exchange rates, directly from the European Central Bank. 

The function "callAPI() makes the actual API call from the code to the website, it requires a url as an argument and uses the requests module in Python to make the actual call. It makes a request to get the currency values of all the countries in JSON format, which it then converts into Python Dictionary format and returns the same nested dictionary

However, the website offers rates wrt only EUR and not wrt USD (The standard) and so, the convertToUSD() function takes a dictionary as an argument and returns the converted dictionary wrt USD.

There is also another API call made for a converter b/w currency codes and countries as mapping them to each other is essential in order to properly receive user input in terms of the country name, as the users are not expected to remember the curr codes of the required currencies.

After the APIs, the first things that are done are calling the updateCurr31 function and the currcountries function. 

The updateCurr31 function is responsible for creating, maintaining and updating a table, which contains all the currency data of the last 31 days. It checks whether the data of all 31 days is present, if not, it deletes the unwanted rows and obtains the new ones. If a required date is not present, it will obtain the relevant data by performing several API calls and entering the data into the table.

The currcountries function is responsible for the correlation b/w countries and their respective currency codes. It maintains a table that stores some data about each country, involving the country name, region, currency name, and currency code. It also checks whether the relevant table is already a part of the SQL database ; if it already is, then it does nothing, if it isn't, then it creates the required table and fills in the records.

After this, certain popular countries such as India, UK, France, etc. are chosen. Their currency data for the past 31 days will be graphically displayed as sample images for any user. However, only 4 random countries from this list will be picked, each with different colours, to be graphed and shown as samples.

Graphing of these sample images is being done with the saveGraph function, a standard graphing function which takes the name of the country and the colour and graphs the currency trend for the past 31 days. The graphing is done by the pyplot package of the matplotlib library.

Next, the landing page is being prepared. A HTML file is being opened, to store the HTML script that houses the landing page. The landing page has 3 boxes, for the name, start date and enddate, and a drop down menu, to select the required countries. The boxes and the drop-down menu are created using HTML code. There are also sample images, as mentioned above, of popular currencies, which are all tabulated wrt USD.

Once the values are entered by the user, and the submit button is pressed, the data is taken and the tab reloads to a new tab. But before that, there are so many tasks done by the program.

Once the data is entered, it is obtained by the HTML form and sent directly to the Flask Server. These values can now be accessed and used to provide the desired outputs. Now that the values are present, potential errors are checked for, including problems with the dates, future dates, start date greater than end date, no countries selected, etc. 

After all the check-steps, a success URL is created, which will be the site of the output page. The URL is one of the parts required for the log table, which keeps track of all the users of this program. The function updateLog inserts new records into the Log Table, and the log table is instrumental for showing the user his previous search as well.

Now, the main part of the program kicks off. A HTML script was started, with the last search option. It allows you to see the number of searches you have done, and also to see your last search

The function responsible for the majority of the program: Collecting the required data using the APIs, creating a user specific table for every unique user and inserting all the values into the required table, is the ultimateFunction. There is a speciality to the ultimate function, being that it doesn't actually use up API calls(limited to 1000 per month) unless absolutely necessary. It searches for similar data in the other tables, searching for identical columns and copying that data into the same table. Very efficient?

After inserting all the data, it must be graphed. And the function saveDateGraph does the job of taking data from tables and graphing the currency values wrt time.

Only after all this, will the output page load, with the requested graphs, load for the user, and that is the end of my project.

In this repo, you will find the source code for the Python part, which incorporates the API calls, SQL calls through the connector, the graphing and the flask parts. Since SQL requires a password, I've only implemented it in my own device, which means you can't expect it to run on your website, but if you change the password in the code, it should run fine. I have also attached the images of how data is actually represented in the website
