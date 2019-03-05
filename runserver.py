#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from project import app,socketio as sc


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    sc.run(app,'0.0.0.0', port=port)
