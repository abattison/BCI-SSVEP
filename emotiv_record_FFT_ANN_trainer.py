#!/usr/bin/python

from fann2 import libfann # update to new format
import sys

connection_rate = 0.25
learning_rate = 0.15
num_input = 48
num_hidden = 25 # something between input and output nodes
num_output = 2

desired_error = 0.0001
max_iterations = 5000000
iterations_between_reports = 10

ann = libfann.neural_net()
ann.create_sparse_array(connection_rate, (num_input, num_hidden, num_output))
ann.set_learning_rate(learning_rate)
ann.set_training_algorithm(1)
ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)

print 'Training network on', len(sys.argv),'files.'

for file_name in sys.argv[1:]:
	# print file_name
	ann.train_on_file(file_name, max_iterations, iterations_between_reports, desired_error)

ann.save("ssvep.net")
