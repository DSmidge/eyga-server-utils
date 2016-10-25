#! /usr/bin/python
# Copyright Eyga.net

# For checking if your mail server is recieving mail.
# Sends mail to SMTP server and checks if it arrived in IMAP inbox.
# Uses starttls for SMTP and tls for IMAP

# Input parameters:
# "mail.server.com" "sender@server.com" "recipient@server2.com" "recipient_password"


# Imports
import sys
import uuid
from email.mime.text import MIMEText
import smtplib
import imaplib
import time


# Read command parameters
if len(sys.argv) == 5:
	server_name = sys.argv[1]
	sender_addr = sys.argv[2]
	recipient_addr = sys.argv[3]
	recipient_pass = sys.argv[4]
	sleep_sec = 30
	uuid = '{' + uuid.uuid1().urn[9:] + '}'
else:
	print("Expected 'server_name', 'sender_email', 'recipient_email', 'recipient_password' for parameters.")
	sys.exit(1)

# Send mail
msg = MIMEText("This is a test to check if mailserver delivers mail to inbox.\nUUID = %s" % (uuid))
msg['From'] = sender_addr
msg['To'] = recipient_addr
msg['Subject'] = "Test"
try:
	s = smtplib.SMTP(server_name)
	s.starttls()
	s.sendmail(sender_addr, [recipient_addr], msg.as_string())
	s.quit()
except:
	print("Error sending mail from %s to %s." % (sender_addr, recipient_addr))
	sys.exit(1)

# Wait for a couple of seconds
time.sleep(sleep_sec)

# Check inbox
mail_found = False
try:
	i = imaplib.IMAP4_SSL(server_name, 993)
	i.login(recipient_addr, recipient_pass)
	i.select()
	typ, data = i.search(None, '(FROM "%s")' % sender_addr)
	for num in data[0].split():
		typ, data = i.fetch(num, '(RFC822)')
		if uuid in data[0][1].decode("utf-8"):
			i.store(num, '+FLAGS', '\\Deleted')
			mail_found = True
	i.close()
	i.logout()
except:
	print("Error reading mail from %s inbox." % (recipient_addr))
	sys.exit(1)
if mail_found == False:
	print("Testing recieving mail to IMAP. Message send to %s with uuid = %s was not found in inbox." % (recipient_addr, uuid))
	sys.exit(1)
