#!/usr/bin/env python
#
# Author: Jake Sokol
# Version: 1.0
#	
# This script collects conntrack count, CPU usage, memory info, uptime, PS info, parses data and appends data to MySQL
#
# Conntrack File Location: "/proc/sys/net/netfilter/nf_conntrack_count
# CPU command: #mpstat -P ALL
# Memory command: #cat /proc/meminfo

import time
import datetime
from datetime import datetime
import MySQLdb
import pexpect
import sys
import os
import re

from config import StartDUTIP,NumberOfUnits,TelnetUser,TelnetPswd,mysql_url,mysql_user,mysql_passwd,mysql_db

# Setting IP range of all unit's based on STARTDUTIP
dutrange = re.split(r'(\.|/)',StartDUTIP)
dot = '.'
first = dutrange[0]
second = dutrange[2]
third =  dutrange[4]
fourth = dutrange[6]
DUTIPx = [first,dot,second,dot,third,dot,fourth]
DUTIP = ''.join(DUTIPx)
txt = 1
txt = str(txt)
deviceinfox = ["DUT",txt,".txt"]
deviceinfo = ''.join(deviceinfox)

startTime = datetime.now()
timestamp = datetime.now() 


def datacollect():	
# Login to Telnet to collect and save device info
	print ("INFO: Starting Data Collection on "+DUTIP)
	time.sleep(3)
	print ("INFO: Starting telnet session on "+DUTIP)
	response = os.system("ping -c 5 "+DUTIP)
	if response == 0:
		session = pexpect.spawn('telnet '+DUTIP)
		session.expect("Login:")
		session.sendline(TelnetUser)
		session.expect("Password:")
		session.sendline(TelnetPswd)		
		session.expect('.*>')

		print "INFO: Collecting DUT's Software Version"
		session.send('\n')
		session.expect('.*>')
		session.sendline('swversion')
		session.expect('.*>')
		swversion = session.after.split()[1]
		ts = time.time()
		swt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		
		print "INFO: Collecting DUT's Serial Number"
		session.send('\n')
		session.expect('.*>')
		session.sendline('gpv InternetGatewayDevice.DeviceInfo.SerialNumber')
		session.expect('.*>')
		serialx = session.after.split("=")[1]
		serial = serialx[:14]
		ts = time.time()
		snwt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')	
	
		print "INFO: Collecting DUT's uptime"
		session.send('\n')
		session.expect('.*>')
		session.sendline('uptime')
		session.expect('.*>')
		ut_outputx = session.after.split("e")[1]
		ut_outputy = ut_outputx[:16]
		ut_output = ut_outputy.lstrip();
		upt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		print "INFO: Collecting PS info"
		session.send('\n')
		session.expect('.*>')
		session.sendline('ps -ef')
		session.expect('.*>')		
		ps = session.after
		ts = time.time()
		pst = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		print "INFO: Collecting Shared Memory"
		session.send('\n')
		session.expect('.*>')
		session.sendline('meminfo')
		session.expect('.*>')		
		smem_output = session.after
		ts = time.time()
		smemt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		print "INFO: Collecting DUT's nf_conntrack_count"	
		session.sendline('sh')
		time.sleep(1)
		session.expect('.*#')
		session.sendline('cat /proc/sys/net/netfilter/nf_conntrack_count')
		session.expect('.*#')
		ct_output = session.after
		ts = time.time()
		connt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		
		print "INFO: Collecting DUT's CPU usage"
		session.send('\n')	
		session.expect('.*#')
		session.sendline('mpstat -P ALL')
		session.expect('.*#')
		cpu_output = session.after
		ts = time.time()
		cput = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		print "INFO: Collecting DUT's memory info"
		session.send('\n')	
		session.expect('.*#')
		session.sendline('cat /proc/meminfo')
		session.expect('.*#')
		mem_output = session.after
		ts = time.time()
		memt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		print ("INFO: Exiting Telnet session on " +DUTIP)
		session.expect('.*')
		session.sendline('exit')
		time.sleep(2)
		session.expect('.*')
		session.sendline('exit')
	

#########################################
# Parsing PEXPECT outputs
#########################################
		
# Prepare conntrack values for mySQL input	
		print "INFO: Parsing data"
		ct_ty = 'CONNTRACK'
		conntrack=''	
		count = ct_output.split()[2]

# Prepare devicetype and current firmware for mySQL input
		devicetype, fwversion = swversion.split("-",1)
		dut = devicetype
		
# Prepare CPU values for mySQL input	
		cp_ty = 'CPU'
		cpu = cpu_output.split()
		cpu0_usr=cpu[34]
		cpu1_usr=cpu[45]
		cpu0_sys=cpu[36]
		cpu1_sys=cpu[47]
		cpu0_idle=cpu[42]
		cpu1_idle=cpu[53]
		
# Prepare Memory values for mySQL input
		mem_ty = 'MEMORY'
		memory = mem_output.split()
		mem_total = memory[3]
		mem_free = memory[6]
		mem_buffer = memory[9]
		mem_cached = memory[12]

# Prepare Uptime value for mySQL input
		ut_ty = 'UPTIME'
		uptime = ut_output

# Prepare PS value for mySQL input
		ps_ty = 'PS'

# Prepare Shared Memory values for mySQL input
		smem_ty = 'SHAREDMEM'
		smem = smem_output.split()
		smem_total = smem[7][:-2]
		smem_usable = smem[12][:-2]
		smem_inused = smem[17][:-2]
		smem_free = smem[22][:-2]


#########################################
# Establish MySQL connection
#########################################
		print "INFO: Appending data to MySQL"
		con = MySQLdb.Connection(host=mysql_url, user=mysql_user, passwd=mysql_passwd, db=mysql_db);
		cur = con.cursor()

			
#########################################
# Data verification and error catching
#########################################
	
# Data verfication: Conntrack Count		
		if (count.isdigit()):
			conntrack = int(count)
			if (conntrack < 10):
				info = 'Conntrack count is less than 10!'
				cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ct_ty, info, timestamp))
				con.commit()				
			else:
				conntrack = 0
				info = 'Conntrack count is either 0 or not collectable!'
				cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ct_ty, info, timestamp))
				con.commit()
		
# Data verfication: CPU Usage
		if (float(cpu0_idle) <= 10 or float(cpu1_idle) <= 10):
			info = 'Warning: CPU usage is near 100%!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, cp_ty, info, timestamp))
			con.commit()
		elif (float(cpu0_idle) <= 30 or float(cpu1_idle) <= 30):
			info = 'Warning: CPU usage is higher than 80%!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, cp_ty, info, timestamp))
			con.commit()
		elif (float(cpu0_idle) <= 50 or float(cpu1_idle) <= 50):
			info = 'Warning: CPU usage is higher than 50%!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, cp_ty, info, timestamp))
			con.commit()	

# Data verfication: Memory Info
		mem_fbc = int(mem_free)+int(mem_buffer)+int(mem_cached)
		if (mem_fbc < 22000):
			info = 'Warning: FREE+BUFFERED+CACHED is lower than expected!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, mem_ty, info, timestamp))
			con.commit()
		if (int(mem_total) < 59500):
			info = 'Warning: Total Memory is lower than 59500KB!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, mem_ty, info, timestamp))
			con.commit()


#Data Verification: Uptime
		if (len(uptime) > 16):
			info = 'Uptime value is not collectable!'
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ut_ty, info, timestamp))
			con.commit()
		else:
			cur.execute("""INSERT INTO alerts(DUT, SERIAL, SWVER, TYPE, INFO, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ut_ty, info, timestamp))
			con.commit()

		
###########################################	
# MySQL Operations: Storing information
###########################################

#Conntrack Table Headers (DUT, SERIAL, SWVERSION, TYPE, DATA, TIMESTAMP)
		cur.execute("""INSERT INTO conntrack(DUT, SERIAL, SWVER, TYPE, DATA, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ct_ty, conntrack, timestamp))
		con.commit()

# CPU Table Headers (DUT, SERIAL, SWVERSION, TYPE, CPU0_USR, 
# CPU1_USR, CPU0_SYS, CPU1_SYS, CPU0_IDLE, CPU1_IDLE, TIMESTAMP)
		cur.execute("""INSERT INTO cpu(DUT, SERIAL, SWVER, TYPE, CPU0_USR, CPU1_USR, CPU0_SYS, CPU1_SYS, CPU0_IDLE, CPU1_IDLE, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, cp_ty, float(cpu0_usr), float(cpu1_usr), float(cpu0_sys), float(cpu1_sys), float(cpu0_idle), float(cpu1_idle), timestamp))
		con.commit()
	
# Memory Table Header (DUT, SERIAL, SWVER, TYPE, MEM_TOTAL, MEM_FREE, 
# MEM_BUFFERS, MEM_CACHED, TIMESTAMP)
		cur.execute("""INSERT INTO memory(DUT, SERIAL, SWVER, TYPE, MEM_TOTAL, MEM_FREE, MEM_BUFFERS, MEM_CACHED, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, mem_ty, mem_total, mem_free, mem_buffer, mem_cached, timestamp))
		con.commit()

# Uptime Table Headers (DUT, SERIAL, SWVER, TYPE, DATA, TIMESTAMP)
		cur.execute("""INSERT INTO uptime(DUT, SERIAL, SWVER, TYPE, DATA, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, ut_ty, uptime, timestamp))
		con.commit()
		
# Shared Memory Table Headers (DUT, SERIAL, SWVER, SMEM_TOTAL, SMEM_USABLE, 
# SMEM_INUSED, SMEM_FREE, TIMESTAMP)
		cur.execute("""INSERT INTO smem(DUT, serial, SWVER, TYPE, SMEM_TOTAL, SMEM_USABLE, SMEM_INUSED, SMEM_FREE, TIMESTAMP) VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (dut, serial, swversion, smem_ty, int(smem_total), int(smem_usable), int(smem_inused), int(smem_free), timestamp))
		con.commit()

# PS Table Headers (DUT, SERIAL, TYPE, PS, TIMESTAMP)
#		cur.execute("""INSERT INTO ps(DUT, SERIAL, SWVER, TYPE, PS, TIMESTAMP) VALUE (%s, %s, %s, %s, %s)""", (dut, serial, swversion, ps_ty, ps, timestamp))
#		con.commit()


# Close MySQL connection
		if con:
			con.close()

loop = NumberOfUnits+1
count = 0
while (count < loop):
	count = count + 1
	datacollect()
	#third = int(third) + 1
	#third = str(third)
	fourth = int(fourth) + 1
	fourth = str(fourth)
	DUTIPx = [first,dot,second,dot,third,dot,fourth]
	DUTIP = ''.join(DUTIPx)
	print '\n','\n'
	time.sleep(2)

print "INFO: Total Executing time: "
print (datetime.now()-startTime)
print "INFO: Goodbye"