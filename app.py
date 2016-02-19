import os

from surgery.receptionist import app


# create our application
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)