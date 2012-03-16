#! /usr/bin/env python
# coding=utf-8
import sae
import urls

app = urls.app

application = sae.create_wsgi_app(app.wsgifunc())

