# -*- coding: utf-8 -*-
"""
"""
import os

from surgery.receptionist import app
from surgery.receptionist import init_db


port = int(os.environ.get('PORT', 5000))
init_db()
app.run(host='0.0.0.0', port=port)