# Forkkit - Pitchfork's album reviews scraper

### Scraper in Python that will integrate my final project with a repository yet to come

---

### **_Installing the scraper_**

1. Clone the repository
2. On the terminal, create a virtual environment by typing   
$ `virtualenv -p python3 .`  
This project was conceived using Python 3.7
3. To load the requirements, type on the terminal  
$ `. bin/activate`  
$ `pip install -r requirements.txt`

### **_Installing the required libraries_**

1. The script uses the excellent mapping tool [peewee](https://github.com/coleifer/peewee) which you probably don't have installed. To get it, type  
$ `pip install peewee`
2. It also uses the [requests.html](https://github.com/psf/requests-html) library for the heavylifting (parsing the HTML pages). To install, hit  
$ `pip install requests-html`  
3. To parse and format the date into the YYYY-MM-DD format instead of 'January 1 2020', so the data is better handled by the SQL database. For that, the library [htmldate](https://github.com/adbar/htmldate) was used. It can be downloaded by installing  
$ `pip install htmldate`  
$ `pip install --upgrade htmldate`  
$ `pip install git+https://github.com/adbar/htmldate.git` 

### **_Creating the database_**

1. To create the database file with the preset tables, type  
$ `python3 models.py`
2. Voilà! You should have now in your folder an `albums.db` file

### **_What exactly the scraper does?_**

- The script parses _all_ [Pitchfork's album reviews](https://pitchfork.com/reviews/albums/). Yes, that's right. There are album reviews dating back from 1999... And they will be parsed too. As of today (May 2020) there are 1,876 published review pages, amounting to 20,141 unique album reviews.
- As you can probably guess, I ain't got no time to browse each one of them manually.
- The scraper therefore parses every single album review published on Pitchfork, collects and inserts the following data into the database:  
  **pitchfork's album review url**  
  **publication date**  
  **album score**  
  **album year**  
  **record label**
  **genre**  
  **review title**  
  **artist**  
  **album**

### **_Running the scraper_**

1. To run the scraper, type on the terminal  
$ `python3 forkkit.py`   
and wait - gathering all this data may take a while!

### **_Changing the variables_**

1. In the `forkkit.py` file, you can change a couple of variables:

- **MAX_WORKERS** = it can be increased to increase the running speed of the script.
- **RANGE** = the number that worked best for me was 1-501, 501-1001, 1001-1501, etc... Iterations of 500 pages per turn, for a smooth run and data-check on my computer.
- **RECURSION_DEPTH** = should be kept at 1 to avoid duplicates.

### Notes

Special thanks to [@nabaskes](https://github.com/nabaskes)
