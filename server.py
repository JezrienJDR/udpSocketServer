import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
         elif 'spawn' in data:
            clients[addr]['spawned'] = 1
            print('SPAWNING!')
        
            GameState = {"cmd": 2, "players": []}
            clients_lock.acquire()
            print (clients)
            for c in clients:
               player = {}
               clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
               player['id'] = str(c)
               player['color'] = clients[c]['color']
               player['position'] = clients[c]['position']
               player['spawned'] = clients[c]['spawned']
               player['disconnected'] = clients[c]['disconnected']
               GameState['players'].append(player)
            s=json.dumps(GameState)
            print(s)
            for c in clients:
               sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
            clients_lock.release()
         elif 'moveName' in data:
            #print ('MOOOOOOOVING')
            #print(data[2:(len(data)-1)])
            moveData = json.loads(data[2:(len(data)-1)])
            #clients[addr]['position']['x'] += moveData['x']
            #print(clients[addr]['position']['x'])
            #print(moveData["x"])
            clients[addr]['position']['x'] = moveData['x']
            clients[addr]['position']['y'] = moveData['y']


            
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['position'] = {"x": random.randrange(0,10,2), "y": random.randrange(0,10,2), "z": random.randrange(0,10,2)}
            clients[addr]['spawned'] = 0
            clients[addr]['disconnected'] = 0
            
            #clients[addr]['id'] = 0
            
            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
            print('CONNECTED!')

            time.sleep(0.5)

            idMessage = {"cmd" : 3, "id":str(addr)}
            im = json.dumps(idMessage)
            sock.sendto(bytes(im, 'utf8'), (addr))
            





def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            #
            message = {"cmd": 4,"id":str(c)}
            #
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()

            m = json.dumps(message)
            for cl in clients:
               sock.sendto(bytes(m,'utf8'), (cl[0],cl[1]))
            
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      #print (clients)
      for c in clients:
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         player['position'] = clients[c]['position']
         player['position']['x'] = clients[c]['position']['x']
         player['position']['y'] = clients[c]['position']['y']
         player['position']['z'] = clients[c]['position']['z']
         player['spawned'] = clients[c]['spawned']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      #print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(0.3)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
