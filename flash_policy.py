#!/usr/bin/env python

import select
import socket
import sys
import oxstarter

oxstarter.starter("flash_policy.pid")

host = 'oxnull.net'
port = 2525
backlog = 5
size = 10240
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(backlog)
input = [server]

while True:
	inputready,outputready,exceptready = select.select(input,[],[])

	for s in inputready:

		if s == server:
			# handle the server socket
			client, address = server.accept()
			input.append(client)
			print 'Client connected: %s'%address[0]
		else:
			# handle all other sockets
			try:
				data = s.recv(size)
				if data.startswith('<policy-file-request/>'): 
					crossdomain = '''<?xml version="1.0"?>
					<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
					<cross-domain-policy>
						<allow-access-from domain="oxnull.net" to-ports="6667" />
					</cross-domain-policy>
					\0'''
					s.send(crossdomain)
					input.remove(s)
					continue
			except socket.error:
				input.remove(s)

