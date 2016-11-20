#!/usr/bin/python
# Copyright Eyga.net
# For python 2.7

# Requires:
# easy_install MySQL-python

# Command example:
# mysql_regex_replace.py --table=wp_posts --column_uid=ID --column=post_content --regex=":[a-zA-Z0-9]{1,15}:" --replace="<!-- {0} -->" > out.sql

# Description:
# Script prepares UPDATE statements for replacing all strings founded by REGEX search.
# Parameters for accessing the database can be specified in mysql.ini or
# can be set with the help of command line arguments.

# TODO:
# * Support for regex groups.


# Import modules
import argparse
import ConfigParser
import MySQLdb
from operator import itemgetter
import os
import re
import sys
from datetime import datetime


# Configuration
class Config(object):
	script_dirpath = None
	
	def __init__(self):
		# Define execution path
		if self.script_dirpath is None:
			script_dirpath = os.path.dirname(sys.argv[0])
			if len(script_dirpath) > 0:
				script_dirpath += "/"
			self.script_dirpath = script_dirpath
		# Set configuration attributes
		self.__connection("mysql.ini")
		self._cmd_arguments()
	
	# Get the path of the configuration file
	def __get_config_filepath(self, config_filename):
		config_filepath = self.script_dirpath + config_filename
		if not os.path.isfile(config_filepath):
			print("Configuration file '" + config_filepath + "' is missing.")
			sys.exit(1)
		return config_filepath
	
	# Read settings from config file
	def __connection(self, config_filename):
		config_filepath = self.__get_config_filepath(config_filename)
		config = ConfigParser.RawConfigParser()
		config.read(config_filepath)
		config_section = "connection"
		self.hostname = config.get(config_section, "hostname")
		self.database = config.get(config_section, "database")
		self.username = config.get(config_section, "username")
		self.password = config.get(config_section, "password")
	
	# Read command arguments
	def _cmd_arguments(self):
		parser = argparse.ArgumentParser(description='Regex replace a value in MySQL table column(s).')
		parser.add_argument('--hostname', help='Hostname', default=self.hostname)
		parser.add_argument('--database', help='Database', default=self.database)
		parser.add_argument('--username', help='Username', default=self.username)
		parser.add_argument('--password', help='Password', default=self.password)
		parser.add_argument('--table', help='Table to search')
		parser.add_argument('--column_uid', help='Name(s) of primary key column(s) - separated my comma')
		parser.add_argument('--column', help='Name of column searched')
		parser.add_argument('--regex', help='Regex expression to search with')
		#parser.add_argument('--regexgrp', required=False, default=1, help='Number of regex group to replace the searched string with')
		parser.add_argument('--replace', required=False, default='', help='String to replace with - searched string (or group value) can be defined by {0}')
		args = parser.parse_args()
		self.hostname = args.hostname
		self.database = args.database
		self.username = args.username
		self.password = args.password
		self.table = args.table
		self.column_uid = args.column_uid
		self.column = args.column
		self.regex = args.regex
		#self.regexgrp = args.regexgrp
		self.replace = args.replace

# Main
config = Config()

# Connect to database
db = MySQLdb.connect(
	host = config.hostname,
	user = config.username,
	passwd = config.password,
	db = config.database)

# Execute query
query = "SELECT `{1}`, `{2}` FROM `{0}` WHERE `{2}` REGEXP '{3}';".format(
	config.table,
	config.column_uid,
	config.column,
	config.regex)
print "-- Server: " + config.hostname
print "-- Database: " + config.database
print "-- Running query: " + query
time_start = datetime.now()
cur = db.cursor()
cur.execute(query)
print "-- Query duration was " + str(round((datetime.now() - time_start).total_seconds(), 1)) + " seconds"

# Get matches from filtered rows
print
print "-- Update queries"
counter = {}
matched = []
rows = cur.fetchall();

# Updates
for row in rows:
	uid = row[0]
	text = row[1]
	matches = re.findall(config.regex, text)
	for match in matches:
		if type(match) is tuple:
			for group in match:
				print "TODO: " + group
		else:
			key = str(match) + ':' + str(uid)
			if key not in matched:
				matched.append(key)
				print "UPDATE `{0}` SET `{3}` = REPLACE(`{3}`, '{4}', '{5}') WHERE `{1}` = '{2}';".format(
					config.table,
					config.column_uid,
					uid,
					config.column,
					match,
					config.replace.format(match))
				if match in counter:
					counter[match] = counter[match] + 1
				else:
					counter[match] = 1

# Statistics
print
print '/*'
elements_s = sorted(counter.items(), key=itemgetter(1), reverse=True)
for elem in elements_s:
	print elem[0] + " : " + str(elem[1]);
print '*/'

# Close database connection
db.close()
