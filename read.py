import pickle

with open('relax.dat', 'rb') as handle:
  b = pickle.load(handle)

print b
