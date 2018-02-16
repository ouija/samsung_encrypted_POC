import websocket
import requests
import socket
import base64
import json
import time
import aes_lib
import uuid
import codecs
import urllib3
import sys
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
os.system('clear')

print()
print('Network Control Script for Samsung H and J Series TVs // @ouija & eclair4151')
print('----------------------------------------------------------------------------')
print()
print()

# Help function
def help():
	print('First, pair the script to your Samsung TV by running the command:')
	print()
	print('python3 samsung.py pair 192.168.1.1')
	print()
	print()
	print('Once paired, you can use this script by passing keycode commands as arguments (and can send multiple keycodes at once)')
	print()
	print('Example: python3 samsung.py KEY_CONTENTS KEY_LEFT KEY_ENTER')
	print()
	print()
	print('Use --keycodes or -codes to display a list of all available keycodes (press "q" to exit viewing keycodes)')
	print()
	print('Example: python3 samsung.py --keycodes')
	print()
	print()
	sys.exit()

# Arguments handlers
if len(sys.argv) > 1:
	for arg in sys.argv[1:]:
		if arg == "-h" or arg == "--h" or arg == "-help" or arg == "--help":
			help()
		elif arg == "--keycodes" or arg == "-keycodes" or arg == "--codes" or arg == "-codes" or arg == "-c" or arg == "--c"or arg == "-k" or arg == "--k":
			os.system( 'less '+script_path+'/keycodes') 
			sys.exit()
else:
	print('Error! No arguments passed.')
	print()
	print('For help, pass the "-h" or "--help" argument')
	print()
	print('Example: python3 samsung.py --help')
	print()
	print()
	sys.exit()

arguments = []
for arg in sys.argv[1:]:
	with open(script_path+'/keycodes') as f:
	    for line in f:
	        if arg.upper() in line:
	        	arguments.append(arg.upper())

if len(arguments) == 0 and sys.argv[1].lower() != "pair":
	print('No valid keycode arguments passed; Exiting..')
	print()
	print('Use --keycodes or -codes to display a list of all available keycodes (press "q" to exit viewing keycodes)')
	print()
	print('Example: python3 samsung.py --keycodes')
	print()
	print()
	sys.exit()
elif sys.argv[1].lower() == "pair":
# Pairing argument
	print('Pairing mode initiated!')
	print()
	# check if IP address passed
	if len(sys.argv) < 3 or len(sys.argv) > 3:
		print('Error: You need to pass the IP address of the Samsung TV you wish to pair with!')
		print()
		print('Example: samsung.py pair 192.168.1.1')
		print()
		print()	
		sys.exit()
	else:
		# validate IP address
		try:
			socket.inet_aton(sys.argv[2])
			# valid IP address

			# pair to the TV
			external_server = 'https://34.210.190.209:5443'
			external_headers = {'Authorization': 'Basic b3JjaGVzdHJhdG9yOnBhc3N3b3Jk', 'Content-Type': 'application/json', 'User-Agent': 'Remotie%202/1 CFNetwork/893.7 Darwin/17.3.0'}
			tv_address = sys.argv[2];

			### STEP 0 START
			device_id = '12345'
			step0_pin_url = 'http://' + tv_address + ':8080/ws/apps/CloudPINPage'
			requests.post(step0_pin_url,data='pin4', timeout=10)
			step0_url = 'http://' + tv_address + ':8080/ws/pairing?step=0&app_id=com.samsung.companion&device_id=12345&type=1'
			r = requests.get(step0_url, timeout=10) #we can prob ignore this response

			### STEP 1 START
			pin = input("Enter TV Pin: ")
			payload = {'pin': pin, 'payload': '', 'deviceId': device_id}
			r = requests.post(external_server + '/step1', headers=external_headers, data=json.dumps(payload), verify=False, timeout=30)
			step1_url = 'http://' + tv_address + ':8080/ws/pairing?step=1&app_id=com.samsung.companion&device_id=12345&type=1'
			step1_response = requests.post(step1_url, data=r.text, timeout=10)
			#### STEP 1 END

			### STEP 2 START
			payload = {'pin': pin, 'payload': codecs.decode(step1_response.text, 'unicode_escape'), 'deviceId': device_id}
			r = requests.post(external_server + '/step2', data=json.dumps(payload), headers=external_headers, verify=False, timeout=30)
			step2_url = 'http://' + tv_address + ':8080/ws/pairing?step=2&app_id=com.samsung.companion&device_id=12345&type=1&request_id=0'
			step2_response = requests.post(step2_url, data=r.text, timeout=10)
			### STEP 2 END

			### STEP 3 START
			payload = {'pin': pin, 'payload': codecs.decode(step2_response.text, 'unicode_escape'), 'deviceId': device_id}
			r = requests.post(external_server + '/step3', data=json.dumps(payload), headers=external_headers, verify=False, timeout=30)
			enc_key = r.json()['session_key']
			session = r.json()['session_id']
			print('session_key: ' + enc_key)
			print('session_id: ' + session)
			step3_url = 'http://' + tv_address + ':8080/ws/apps/CloudPINPage/run'
			requests.delete(step3_url, timeout=10)
			### STEP 3 END

			print('waiting for a sec...')
			time.sleep(2)

			## STEP 4 START   WEBSOCKETS
			millis = int(round(time.time() * 1000))
			step4_url = 'http://' + tv_address + ':8000/socket.io/1/?t=' + str(millis)
			websocket_response = requests.get(step4_url, timeout=10)
			websocket_url = 'ws://' + tv_address + ':8000/socket.io/1/websocket/' + websocket_response.text.split(':')[0]

			time.sleep(1)
			print('sending KEY_VOLDOWN command!')
			aesLib = aes_lib.AESCipher(enc_key, session)
			connection = websocket.create_connection(websocket_url)
			time.sleep(0.35)
			connection.send('1::/com.samsung.companion')
			time.sleep(0.35)
			r = connection.send(aesLib.generate_command('KEY_VOLDOWN'))
			time.sleep(0.35)
			connection.close()
			print('sent')
			## STEP 4 END

			## STEP 5 WRITE CONFIG
			text_file = open(script_path+"/config", "w")
			text_file.write(sys.argv[2])
			text_file.write("\n%s" % enc_key)
			text_file.write("\n%s" % session)
			text_file.close()
			print()
			print('PAIRING COMPLETE! You should be able to run the script now simply by passing keycode commands as arguments')
			print()
			print('Example: python3 samsung.py KEY_CONTENTS')
			print()
			print('Use --keycodes or -codes to display a list of all available keycodes')
			print()
			print('Example: python3 samsung.py --keycodes')
			print()
			print()

		except socket.error:
		    # not valid
		    print('Error: Invalid IP address detected; Please try again.')
		    print()
		    print()
		sys.exit()



# Main script

### STEP 1 - LOAD IN CONFIG VARIABLES IF CONFIG FILE EXISTS
try:
	with open (script_path+"/config", "r") as myfile:
		data=myfile.readlines()

		tv_address = data[0].replace('\n', '')
		enc_key = data[1].replace('\n', '')
		session = data[2].replace('\n', '')

		print('tv ip address: ' + tv_address)
		print('session key: ' + enc_key)
		print('session id: ' + session)
		### STEP 1 END


		## STEP 2 START   WEBSOCKETS
		millis = int(round(time.time() * 1000))
		step4_url = 'http://' + tv_address + ':8000/socket.io/1/?t=' + str(millis)
		websocket_response = requests.get(step4_url)
		websocket_url = 'ws://' + tv_address + ':8000/socket.io/1/websocket/' + websocket_response.text.split(':')[0]
		print()
		print('connecting to device..')

		time.sleep(1)
		#print('sending %s command to device..' % sys.argv[1])
		aesLib = aes_lib.AESCipher(enc_key, session)
		connection = websocket.create_connection(websocket_url)
		time.sleep(0.35)
		connection.send('1::/com.samsung.companion')
		time.sleep(0.35)
		# send all parameters specified
		if len(arguments) > 0:
			for arg in arguments[0:]:
				print('sending %s command to device..' % arg)
				r = connection.send(aesLib.generate_command(arg))
				# additional delay after issuing 'smart apps' command as it is slow to open
				if arg == "KEY_CONTENTS":			
					time.sleep(2)
				else:
					time.sleep(1)

		connection.close()
		print('sent successfully!')

		## STEP 4 END

		print()
		print()
except IOError:
	# ERROR: NO CONFIG FILES
	print('Error: No configuration file found!')
	print()
	print('You need to pair the script to your Samsung TV by running the command:')
	print()
	print('python3 samsung.py pair <ip address of samsung tv>')
	print()
	print()
	sys.exit()