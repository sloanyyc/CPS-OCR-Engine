#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
labs = {}
for x in range(33, 126):
  labs[x-33] = str(chr(x))
pickle.dump(labs, open('my_labs', 'wb'))

