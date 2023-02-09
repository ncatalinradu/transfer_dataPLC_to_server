import snap7, io, paramiko, time
from datetime import datetime
from paramiko import SSHClient
from scp import SCPClient

#init data
Posturi_lucru = open('C:\python\Scripts\monitorizare\posturi.txt','r').readlines()
nr_posturi = len(Posturi_lucru)
Nume_PLC = []
Post_lucru = []
for post in Posturi_lucru:
    linie = post.split('\n')
    valori = linie[0].split(',')
    Nume_PLC.append(valori[0])
    Post_lucru.append(valori[1])

####################
#read data from PLC#
####################
server = 'x.x.x.x'      #destination server
port = 'x'              #port acces SCP
user = 'user'           #user
password = 'pass'       #pass

Conectare_PLC = open('C:\python\Scripts\monitorizare\plc.txt','r').readlines()
print(Conectare_PLC)
conectare = Conectare_PLC[0].split(';')
IP = conectare[0]
RACK = int(conectare[1])
SLOT = int(conectare[2])
DB_nr = int(conectare[3])
Start = int(conectare[4])
Size = int(conectare[5])

plc = snap7.client.Client()
plc.connect(IP,RACK,SLOT)

state = plc.get_cpu_state() #read stat PLC run/stop/error
print(f'State:{state}')

for y in range(10):
    fisier_buffer = io.StringIO()
    ora_actuala=datetime.now()
    print ("Esantionul de achizitie nr :", y, ora_actuala)
    for esantion in range(100):
        db = plc.db_read(DB_nr, Start, Size)
        now=datetime.now()
        for post in Posturi_lucru:
            Byte_TCY=db[1] 
            Byte_Div=db[2] 
            Byte_Def=db[3] 
            linie = str(Byte_TCY) + ";" + str(Byte_Div) + ";" + str(now) + ";" + str(Byte_Def) + "\n"
            fisier_buffer.write(linie)
        time.sleep(0.180)
                
    nume_fisier = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    cale = '/usr/sbin/scripts/date/' + nume_fisier + '.txt'
    fisier_buffer.seek(0)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, port, user, password)
    with SCPClient(ssh.get_transport()) as scp:
        scp.putfo(fisier_buffer, cale)
    fisier_buffer.close()
print("ok")
