import os
import socket
import unittest
import pickle
from multiprocessing.connection import Client
from multiprocessing import Lock
PORT = 17000

def is_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = True
    try:
        sock.bind(('localhost', port))
        result = False
    except:
        print("Port is in use")
    sock.close()
    return result

session_list = []
pid_list = []
session_lock_pid = []
session_lock = Lock()
bus_lock = Lock()

def init():
    print('init...')
    class RPCHandler:
        def __init__(self):
            self._functions = { }

        def register_function(self, func):
            self._functions[func.__name__] = func

        def handle_connection(self, connection):
            try:
                while True:
                    # Receive a message
                    func_name, args, kwargs = pickle.loads(connection.recv())
                    # Run the RPC and send a response
                    try:
                        r = self._functions[func_name](*args,**kwargs)
                        connection.send(pickle.dumps(r))
                    except Exception as e:
                        connection.send(pickle.dumps(e))
            except EOFError:
                pass

    from multiprocessing.connection import Listener
    from threading import Thread

    def rpc_server(handler, address, authkey):
        sock = Listener(address, authkey=authkey)
        while True:
            client = sock.accept()
            t = Thread(target=handler.handle_connection, args=(client,))
            t.daemon = True
            t.start()

    # Some remote functions
    def add_session(session):
        pass

    def add_pid(pid):
        if pid not in pid_list:
            pid_list.append(pid)
        print('add_pid(pid=[{}]) pid_list=[{}]'.format(str(pid),str(pid_list)))
        return len(pid_list)
    
    def acquire_session_lock(pid):
        bus_lock.acquire()
        add_pid(pid)
        global session_lock_pid
        print('acquire_session_lock(pid=[{}]) session_lock_pid=[{}]'.format(str(pid),str(session_lock_pid)))
        bus_lock.release()
        session_lock.acquire()
        session_lock_pid = pid    
        print('acquire_session_lock success')
        return True

    def release_session_lock(pid):
        bus_lock.acquire()
        add_pid(pid)
        global session_lock_pid
        print('release_session_lock(pid=[{}]) session_lock_pid=[{}]'.format(str(pid),str(session_lock_pid)))
        if session_lock_pid == pid:
            session_lock_pid = -1
            bus_lock.release()
            session_lock.release()
            print('release_session_lock success')
            return True
        bus_lock.release()
        print('release_session_lock error')
        return False

    # Register with a handler
    handler = RPCHandler()
    handler.register_function(add_pid)
    handler.register_function(acquire_session_lock)
    handler.register_function(release_session_lock)

    def get_tasks():
        return pid_list
    handler.register_function(get_tasks)


    # Run the server
    rpc_server(handler, ('localhost', PORT), authkey=b'lxx')

if is_port_in_use(PORT):
    print('port:'+str(PORT)+' is already in use')
    pass
else:
    pass
    init()