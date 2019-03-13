from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///cars.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Delete CarsCompanyName if exisitng.
session.query(CarCompanyName).delete()
# Delete CarName if exisitng.
session.query(CarName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="Mohana Pragada", email="pmohana683@gmail.com",
             picture='http://www.enchanting-costarica.com/wp-content/'
             'uploads/2018/02/jcarvaja17-min.jpg')
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample car companys
Cmp1 = CarCompanyName(name="TataTiago",
                      user_id=1)
session.add(Cmp1)
session.commit()

Cmp2 = CarCompanyName(name="FordFreestyle",
                      user_id=1)
session.add(Cmp2)
session.commit

Cmp3 = CarCompanyName(name="Honda Amaze",
                      user_id=1)
session.add(Cmp3)
session.commit()

Cmp4 = CarCompanyName(name="Maruti Suzuki Dzire",
                      user_id=1)
session.add(Cmp4)
session.commit()

Cmp5 = CarCompanyName(name="CentySports",
                      user_id=1)
session.add(Cmp5)
session.commit()

Cmp6 = CarCompanyName(name="RMZ Lamborgini",
                      user_id=1)
session.add(Cmp6)
session.commit()

# Populare a cars with models for testing
# Using different users for cars names year also
N1 = CarName(name="Maruti Suziki Baleno",
             color="black",
             cc="200cc",
             price="7,00,650",
             cartype="car",
             date=datetime.datetime.now(),
             carcompanynameid=1,
             user_id=1)
session.add(N1)
session.commit()

N2 = CarName(name="Maruti Suzuki Swift",
             color="blue",
             cc="505cc",
             price="4,25,000",
             cartype="car",
             date=datetime.datetime.now(),
             carcompanynameid=2,
             user_id=1)
session.add(N2)
session.commit()

N3 = CarName(name="Lamborgini Veneno",
             color="ash",
             cc="670cc",
             price="10,73,650",
             cartype="Racing Car",
             date=datetime.datetime.now(),
             carcompanynameid=3,
             user_id=1)
session.add(N3)
session.commit()

N4 = CarName(name="Mercedes Benz W124",
             color="purple",
             cc="1055cc",
             price="90,55,950",
             cartype="Benz Car",
             date=datetime.datetime.now(),
             carcompanynameid=4,
             user_id=1)
session.add(N4)
session.commit()

N5 = CarName(name="Ferrari",
             color="blue",
             cc="620cc",
             price="10,25,650",
             cartype="car",
             date=datetime.datetime.now(),
             carcompanynameid=5,
             user_id=1)
session.add(N5)
session.commit()

N6 = CarName(name="Ambassader",
             color="white",
             cc="1000cc",
             price="11,73,000",
             cartype="car",
             date=datetime.datetime.now(),
             carcompanynameid=6,
             user_id=1)
session.add(N6)
session.commit()

print("Your cars database has been inserted!")
