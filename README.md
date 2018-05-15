# Network Control Script for Samsung H and J Series TVs

This forked version of https://github.com/eclair4151/samsung_encrypted_POC/ consists of a single script used for pairing and sending commands over a network to H and J series Samsung TVs that use encrypted communication.

Currently uses a 3rd party server using the smartview DLLs to figure out the encryption.<br>
*(source can be found here: https://github.com/eclair4151/SamsungEncryptServer)*  

###### Requirements:

* Python3
* websocket-client
* requests
* pyCryptodome (preferred) or pycrypto


###### How to use:

First, pair the script to your Samsung H/J Series TV by running the command:

`python3 samsung.py pair <ip address of tv>`

Once paired, the configuration is saved locally and you can then simply use this script by passing keycode commands as arguments (and can also send multiple keycodes at once!)

*Example:* `python3 samsung.py KEY_CONTENTS KEY_LEFT KEY_ENTER`

Use `--keycodes` or `-codes` to display a list of all available keycodes (press `q` to exit viewing keycodes)

*Example:* `python3 samsung.py --keycodes`

View the list of available keycode arguments [here](keycodes)


###### Troubleshooting:  

Note the the following TV Models are most likely incompatible for one reason or another

*J4xxx, J50xx, J51xx, J52xx, J53xx, UNxxJ6200, J6201, J6203, J620D   
H4xxx, H510x, H52xx, H53x3, H5403, H6003, H61x3, H6201, H6203, S9, S9C*  

Ensure you are using **Python3** and have **websocket-client** and either **pyCryptodome** or **pycrypto** modules installed

*Example:* `pip3 install websocket-client pyCryptodome`


###### Thanks: 

A huge thank you to [eclair4151](https://github.com/eclair4151) for doing the majority of the work in regards to this script;  I just made it more user friendly, but he is responsible for the underlying code that made this all possible and deserves 100% of the credit!
