from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

if __name__ =='__main__':
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
    myFirstRestaurant = Restaurant(name='Pizza Palace')
    session.add(myFirstRestaurant)
    session.commit()
    print(session.query(Restaurant).all())

