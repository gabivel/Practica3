import socket
import sys
import time
import threading
import os
import struct


IP = "192.168.1.79"
PORT = 1121
BUFFER_SIZE = 1024

def accept_client(TCPServerSocket):
    while True:
        Client_conn, Client_addr = TCPServerSocket.accept()
        #Crear un hilo independiente para cada cliente
        thread = threading.Thread(target=worker, args=(Client_conn,))
        thread.start()

def verificaUsuario(usuario):
	with open('users.txt') as temp_f:
		lineas = temp_f.readlines()
		for linea in lineas:
			if usuario in linea:
				return True
		return False

def verificaContrasena(usuario,passwrd):
	with open('users.txt') as temp_f:
		lineas = temp_f.readlines()
		for linea in lineas:
			if (usuario + ' ' + passwrd) in linea:
				return True
		return False

def obtenerDelServidor(file_name,content,puerto,Client_conn):
	TCPDataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCPDataSocket.connect((IP, int(puerto)))
	#mandar que se abrio la conexion
	Client_conn.send(str.encode("125 conexion de datos abierta, comienza transferencia"))
	TCPDataSocket.send(struct.pack("i", os.path.getsize(file_name)))
	print("Sending file...")
	#content = open(file_name, "rb")
    # Again, break into chunks defined by BUFFER_SIZE
	l = content.read(BUFFER_SIZE)
	while l:
		TCPDataSocket.send(l)
		l = content.read(BUFFER_SIZE)
	content.close()
	TCPDataSocket.close()

def guardarEnServidor(output_file,puerto,Client_conn):
	TCPDataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCPDataSocket.connect(("192.168.1.89",int(puerto)))
	Client_conn.send(str.encode("125 conexion de datos abierta, comienza transferencia"))
	file_size = struct.unpack("i", TCPDataSocket.recv(4))[0]
	bytes_recieved = 0
	print("\nDownloading...")
	while bytes_recieved < file_size:
		l = TCPDataSocket.recv(BUFFER_SIZE)
		output_file.write(l)
		bytes_recieved += BUFFER_SIZE
	output_file.close()
	TCPDataSocket.close()
	print("Successfully downloaded")

def quit(Client_conn):
	Client_conn.send(str.encode("\n221 cerrando conexion de control"))
    # Close and restart the server
	Client_conn.close()
    #TCPServerSocket.close()


def worker(Client_conn):
	Client_conn.send(str.encode("220 Servicio listo"))
	#while True:
	print("\nEsperando por instruccion")
	data = Client_conn.recv(BUFFER_SIZE)
	data = data.decode('utf-8')
	print("\nInstruccion recibida{}".format(data))
	# Check the command and respond correctly
	if data[:4].upper() == "USER":
		if verificaUsuario(data[5:]):
			#usuario existe 
			Client_conn.send(str.encode("331 Usuario ok, necesita una contraseña"))
			print("\nEsperando por instruccion de password")
			pwd = Client_conn.recv(BUFFER_SIZE)
			pwd = pwd.decode('utf-8')
			if pwd[:4].upper() == "PASS":
	        		if verificaContrasena(data[5:],pwd[5:]):
	        			Client_conn.send(str.encode("230 Usuario conectado, continue"))
	        			#os.chdir("C:/Users/Velasco/Documents/Redes2/FTP/"+data[5:])
	        			print("\nusuario y contraseña correcta")
	        			while True:
	        				print("Usuario {} puede transferir archivos".format(data[5:]))
	        				command = Client_conn.recv(BUFFER_SIZE)
	        				command = command.decode('utf-8')
	        				if command[:4].upper() == "RETR":
	        					try:
	        					# Check the file exists
	        						content = open(command[5:], "rb")
	        						Client_conn.send(str.encode("150 Fichero correcto, se abrira conexion de datos"))
	        					except:
	        						print("Couldn't open file. Make sure the file name was entered correctly.")
	        					print("espero puerto para datos")
	        					PORT_DATA = Client_conn.recv(BUFFER_SIZE)
	        					PORT_DATA = PORT_DATA.decode('utf-8')
	        					obtenerDelServidor(command[5:],content,PORT_DATA[5:],Client_conn)
	        				elif command[:4].upper() == "STOR":
	        					output_file = open(command[5:], "wb")
	        					Client_conn.send(str.encode("150 Fichero correcto, se abrira conexion de datos"))
	        					print("espero puerto para datos")
	        					PORT_DATA = Client_conn.recv(BUFFER_SIZE)
	        					PORT_DATA = PORT_DATA.decode('utf-8')
	        					print(PORT_DATA)
	        					puerto = PORT_DATA[5:]
	        					puerto = puerto.strip()
	        					print(puerto)
	        					print(type(puerto))
	        					#if PORT_DATA[:4].upper() == "PORT":
	        					guardarEnServidor(output_file,puerto,Client_conn)
	        				elif command[:4].upper() == "QUIT":
	        					quit(Client_conn)
	        					break
	        		else:
	        			Client_conn.send(str.encode("332 Necesita una cuenta para entrar al sistema"))
	        			print("Contraseña incorrecta, intente en conexion nueva") 
		else:
			#usuario no existe
			Client_conn.send(str.encode("332 Necesita una cuenta para entrar al sistema"))
			print("no se encontro el usuario")
	elif data == "QUIT":
		quit(Client_conn)

TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPServerSocket.bind((IP, PORT))
TCPServerSocket.listen(3)
print("\nBienvenido al servidor FTP.\nEn espera")
accept_client(TCPServerSocket)