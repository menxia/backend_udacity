from http.server import BaseHTTPRequestHandler, HTTPServer 
from urllib.parse import parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output.encode())
                return 
            
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' action = '/restaurants/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output.encode())
            
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += "Are you sure you want to delete %s?"%myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' action = '/restaurants/%s/delete' >" % restaurantIDPath
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output.encode())

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
                for restaurant in restaurants:
                    output += restaurant.name 
                    output += '</br>'
                    output += "<a href='/restaurants/%s/edit'>Edit</a>" % restaurant.id 
                    output += "</br>"
                    output += "<a href ='/restaurants/%s/delete'>Delete </a>" % restaurant.id 
                    output += "</br></br></br>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                # print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/edit'):
                length = int(self.headers.get('Content-length', 0))

                # Read the correct amount of data from the request.
                data = self.rfile.read(length).decode()
                # Extract the "message" field from the request data.
                newName = parse_qs(data)["newRestaurantName"][0]

                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    myRestaurantQuery.name = newName
                    session.add(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            
            elif self.path.endswith('/delete'):
                length = int(self.headers.get('Content-length', 0))
                # Extract the "message" field from the request data.
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            


            elif self.path.endswith('/new'):          
                length = int(self.headers.get('Content-length', 0))

                # Read the correct amount of data from the request.
                data = self.rfile.read(length).decode()
                # Extract the "message" field from the request data.
                name = parse_qs(data)["newRestaurantName"][0]
                
                newRestaurant = Restaurant(name=name)
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        # print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()

