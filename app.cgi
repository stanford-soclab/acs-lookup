#!/usr/bin/env python
from wsgiref.handlers import CGIHandler
from acs_lookup import app

CGIHandler().run(app)