import wsgi
from marketapp.models import userModel
f = userModel(name = 'Bob Smith', password = 'supersecure', email ='bwillins@umbc.edu', umbc_id='aa12345')
u = userModel(name = 'Steve Jerbs', password = 'supersecure', email ='stevie@umbc.edu', umbc_id='aa12346')
w = userModel(name = 'Steve Jorbs', password = 'password', email ='stevie@umbc.edu', umbc_id='aa12341')
#chown www-data /home/nulp/code/django/marketapp
#chown www-data /home/nulp/code/django/marketapp/db.sqlite3
