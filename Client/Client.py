import socket
import sys
import os
import struct

IP = "192.168.1.79" 
PORT = 1121 
buffer_size = 1024

def user(user):
	try:
        #enviando comando USER
		TCPClientSocket.send(str.encode(user))
	except:
		print("Couldn't make server request. Make sure a connection has bene established.")
		return
	
	# Esperando estado del servidor(if the user exists)
	estado = TCPClientSocket.recv(buffer_size)
	estado = estado.decode('utf-8')
	print(estado)
	if estado[:3] == "331":
		return True
	elif estado[:3] == "332":
		return False

def passwrd(passwrd):
	try:
        # Enviando comando PASS
		TCPClientSocket.send(str.encode(passwrd))
	except:
		print("Couldn't make server request. Makesure a connection has bene established.")
		return
	
	# Esperando estado del servidor(password is correct)
	estado = TCPClientSocket.recv(buffer_size)
	estado = estado.decode('utf-8')
	print(estado)
	if estado[:3] == "230":
		return True
	elif estado[:3] == "332":
		return False

def port_data(port_data):
	try:
        # Enviando comando PASS
		TCPClientSocket.send(str.encode(port_data))
	except:
		print("Couldn't make server request. Make sure a connection has bene established.")
		return

def retr(file_name,peticion):
	try:
        # Enviando comando
		TCPClientSocket.send(str.encode(peticion))
	except:
		print("Couldn't make server request. Make sure a connection has bene established.")
		return
	estado = TCPClientSocket.recv(buffer_size)
	estado = estado.decode('utf-8')
	print(estado)
	PORT_DATA = input('Ingrese comando PORT X: ')
	if PORT_DATA[:4].upper() == "PORT":
		DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		DataSocket.bind(("192.168.1.89", int(PORT_DATA[5:])))
		DataSocket.listen()
		port_data(PORT_DATA)
		conn, addr = DataSocket.accept()
		estado = TCPClientSocket.recv(buffer_size)
		estado = estado.decode('utf-8')
		print(estado)
		file_size = struct.unpack("i", conn.recv(4))[0]
		output_file = open(file_name, "wb")
		bytes_recieved = 0
		print("\nDownloading...")
		while bytes_recieved < file_size:
			l = conn.recv(buffer_size)
			output_file.write(l)
			bytes_recieved += buffer_size
		output_file.close()

		DataSocket.close()
		print("Successfully downloaded {}".format(file_name))
	else:
		print("comando incorrecto, operacion cancelada")

def stor(file_name,peticion):
	try:
        # Enviando comando PASS
		TCPClientSocket.send(str.encode(peticion))
	except:
		print("Couldn't make server request. Make sure a connection has bene established.")
		return
	estado = TCPClientSocket.recv(buffer_size)
	estado = estado.decode('utf-8')
	print(estado)
	PORT_DATA = input('Ingrese comando PORT X: ')
	if PORT_DATA[:4].upper() == "PORT":
		DataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		DataSocket.bind(("192.168.1.89", int(PORT_DATA[5:])))
		DataSocket.listen()
		port_data(PORT_DATA)
		conn, addr = DataSocket.accept()
		estado = TCPClientSocket.recv(buffer_size)
		estado = estado.decode('utf-8')
		print(estado)
		try:
			# Check the file exists
			content = open(file_name, "rb")
		except:
			print("Couldn't open file. Make sure the file name was entered correctly.")
		conn.send(struct.pack("i", os.path.getsize(file_name)))
		print("Sending file...")
		l = content.read(buffer_size)
		while l:
			conn.send(l)
			l = content.read(buffer_size)
		content.close()
		conn.close()
		DataSocket.close()
	else:
		print("comando incorrecto, operacion cancelada")

def quit():
    TCPClientSocket.send(str.encode("QUIT"))
    # Wait for server go-ahead
    print(TCPClientSocket.recv(buffer_size).decode('utf-8'))

    TCPClientSocket.close()
    print("Server connection ended")


print("\nBienvenido al cliente FTP para transferencia de datos. \n\nPara transferir archivos, ingrese usuario y contraseña\n\nComandos disponibles\nUSER           : Connect to server\nPASS           : Connect to server\nSTOR file_path : envia file\nRETR file_path : Download file\nPORT number		: data_port\nQUIT           : Exit")
TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPClientSocket.connect((IP, PORT))
estado = TCPClientSocket.recv(buffer_size)
estado = estado.decode('utf-8')
print(estado)

#while True:	
    # Listen for a command
prompt = input("\nComando> ")
if prompt[:4].upper() == "USER":
	if user(prompt):
		print("Se espera pass")
		pwd= input("\nComando> ")
		if pwd[:4].upper() == "PASS":
			if passwrd(pwd):
				os.chdir("C:/Users/Velasco/Documents/Redes2/FTP/"+prompt[5:])
				while True:
					print("\nPuede realizar tranferencia de archivos ")
					command = input("Comando> ")
					if command[:4].upper() == "RETR":
						file_name = command[5:]#Se envia la peticion
						retr(file_name,command)
					elif command[:4].upper() == "STOR":
						file_name = command[5:]
						stor(file_name,command)
					elif command.upper() == "QUIT":
						quit()
						break
					else:
						print("Command not recognised; please try again")
		else:
			print("Command not recognised; please try again")
elif prompt[:4].upper() == "QUIT":
	quit()
	#	break
else:
	print("Command not recognised; please try again")