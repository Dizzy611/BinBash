#!/usr/bin/env python
# BinBash, IRC quote bot.
# BinBash is Copyright 2010 Dylan Morrison
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Edit these
SERVER="irc.foo.org" # Hostname of the server the bot is connecting to
PORT=6667 # Port the bot is connecting to
NICK="BinBash" # Nickname of the bot
IDENT="BinBash" # Ident/Username of the bot
CHANNEL="#bar" # Channel for the bot to join
REALNAME="BinBash" # Realname of the bot
# Do not edit below here

import os
import sys
import socket
import string
import re
from random import choice, randint

def slicestring(input):
	if len(input) < 440:
		return [input]
	else:
		return filter(lambda x: x != '', re.split("(.{1,440} )", input+" "))

readbuffer=""

s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))

while 1:
    readbuffer=readbuffer+s.recv(10)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop( )

    for line in temp:
        line=string.rstrip(line)
        line=string.split(line)
        if(line[0]=="PING"):
            s.send("PONG %s\r\n" % line[1])
	if(line[1]=="PING"):
	    s.send("PONG %s\r\n" % line[2])
	if(line[1]=="376"):
	    s.send("JOIN %s\r\n" % CHANNEL)
	    # pass
	if(line[1]=="PRIVMSG"):
	    origin = line[0].split(':')[1]
	    hostmask = origin.split('!')[1]
	    nick = origin.split('!')[0]
	    ident = hostmask.split('@')[0]
	    address = hostmask.split('@')[1]
	    dest = line[2]

	    # Some voodoo here to turn the message received into one 
	    # long string without initial ":". 
	    msg = string.join(line[3:], " ")
	    msglist = msg.split(':')
	    del msglist[0]
	    msg = string.join(msglist, ":")
	    # End voodoo
	    splitmsg = msg.split(' ')
	    command = splitmsg[0]
	    recom = re.match("^!([a-zA-Z0-9]+)bash$", command)
	    if recom != None:
		try: 
			bashfile = open("bashes/" + recom.group(1) + ".txt")
			lineslist = bashfile.readlines()
			if (len(splitmsg) == 2) and (re.match("^[0-9]+$", splitmsg[1]) != None) and (int(splitmsg[1]) > 0) and (int(splitmsg[1]) < len(lineslist)):
				linenum = int(splitmsg[1])
				if linenum == None:
					if dest.lower() != NICK.lower():
						s.send("PRIVMSG " + dest + " :Malformed command. (Invalid line number)\r\n")
					else:
						s.send("PRIVMSG " + nick + " :Malformed command. (Invalid line number)\r\n")
				else:
					linenum = linenum - 1
					if dest.lower() != NICK.lower():
						slicelist = slicestring(lineslist[linenum].rstrip())
						s.send("PRIVMSG " + dest + " :" + str(linenum + 1) + ". " + slicelist[0] + "\r\n")
						del slicelist[0]
						if slicelist != []:
							for tmpline in slicelist:
								s.send("PRIVMSG " + dest + " :" + tmpline + "\r\n")
					else:
						slicelist = slicestring(lineslist[linenum].rstrip())
						s.send("PRIVMSG " + dest + " :" + str(linenum + 1) + ". " + slicelist[0] + "\r\n")
						del slicelist[0]
						if slicelist != []:
							for tmpline in slicelist:
								s.send("PRIVMSG " + nick + " :" + tmpline + "\r\n")
			else: 					
				linenum = randint(0, len(lineslist) - 1)
				if dest.lower() != NICK.lower():
					slicelist = slicestring(lineslist[linenum].rstrip())
					s.send("PRIVMSG " + dest + " :" + str(linenum + 1) + ". " + slicelist[0] + "\r\n")
					del slicelist[0]
					if slicelist != []:
						for tmpline in slicelist:
							s.send("PRIVMSG " + dest + " :" + tmpline + "\r\n")

				else:
					slicelist = slicestring(lineslist[linenum].rstrip())
					s.send("PRIVMSG " + dest + " :" + str(linenum + 1) + ". " + slicelist[0] + "\r\n")
					del slicelist[0]
					if slicelist != []:
						for tmpline in slicelist:
							s.send("PRIVMSG " + nick + " :" + tmpline + "\r\n")

		except IOError:
			if dest.lower() != NICK.lower():
				s.send("PRIVMSG " + dest + " :Sorry, " + recom.group(1) + " is not a valid bash file: IOError.\r\n")
			else:
				s.send("PRIVMSG " + nick + " :Sorry, " + recom.group(1) + " is not a valid bash file: IOError.\r\n")
	    if (command == "!addquote") and (len(splitmsg) >= 3) and (re.match("^[a-zA-Z0-9]+$", splitmsg[1]) != None):
		try:
			if os.path.exists("bashes/" + splitmsg[1] + ".txt") == True:
				output = open("bashes/" + splitmsg[1] + ".txt", "a")
				output.write(string.join(splitmsg[2:], " ") + "\n")
				output.close()
			else:
				output = open("bashes/" + splitmsg[1] + ".txt", "a")
				output.write(string.join(splitmsg[2:], " ") + "\n")
				output.close()

			if dest.lower() != NICK.lower():
				s.send("PRIVMSG " + dest + " :Quote successfully added to " + splitmsg[1] + "bash.\r\n")
			else:
				s.send("PRIVMSG " + nick + " :Quote successfully added to " + splitmsg[1] + "bash.\r\n")
		except IOError:
			if dest.lower() != NICK.lower():
				s.send("PRIVMSG " + dest + " :IOError adding quote. Is " + splitmsg[1] + "bash a valid bash file? Ask Insidious.\r\n")
			else:
				s.send("PRIVMSG " + nick + " :IOError adding quote. Is " + splitmsg[1] + "bash a valid bash file? Ask Insidious.\r\n")
				
	    if command == "!bashes":
			liststring = string.join(os.listdir("bashes/"), " ")
			liststring = re.sub(".txt", "", liststring)
			if dest.lower() != NICK.lower():
				s.send("PRIVMSG " + dest + " :Bashes currently in my list: " + liststring + "\r\n") 
			else:
				s.send("PRIVMSG " + nick + " :Bashes currently in my list: " + liststring + "\r\n") 
