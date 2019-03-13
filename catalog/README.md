# Item Catalog Car Garage Web App
By MohanaPragada
This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).


## In This Project
 Three Python files are their 
 Project.py
 Data_Setup.py
 db_init.py
 And HTML Files are Placed in the Templates folder by using the Flask Applocation

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth2client
5. Flask Framework
6. DataBaseModels


## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)



## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd /vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run pip install requests
7. Setup application database `python /Car Garage/Data_Setup.py`
8. Insert sample data `python /Car Garage/db_init.py`
9. Run application using `python /Car Garage/project.py`
10.Access the application locally using http://localhost:8000


### JSON Codes
The following are open to the public:

1.Cars Catalog JSON: `/CarStore/JSON`
    - Displays the whole cars models catalog. Car Categories and all models.

2.Car Categories JSON: `/carStore/carCategories/JSON`
    - Displays all Cars categories
3.All Car Editions: `/carStore/cars/JSON`
	- Displays all Car Models

4.Car Edition JSON: `/carStore/<path:car_name>/cars/JSON`
    - Displays Car models for a specific Car category

5.Car Category Edition JSON: `/carStore/<path:car_name>/<path:edition_name>/JSON`
    - Displays a specific Car category Model.

## Miscellaneous

This project is inspiration from https://github.com/YVenkatesh7/catalog/blob/master/catalog
