from tensorflow.python.pywrap_tensorflow_internal import *
#from tensorflow.python.rpc_lxx import *
import os
import socket
import unittest
import pickle
from multiprocessing.connection import Client
PORT = 17000

def add_pid():
    c = Client(('localhost', PORT), authkey=b'lxx')
    proxy = RPCProxy(c)
    return proxy.add_pid(os.getpid())

def acquire_session_lock():
    c = Client(('localhost', PORT), authkey=b'lxx')
    proxy = RPCProxy(c)
    return proxy.acquire_session_lock(os.getpid())

def release_session_lock():
    c = Client(('localhost', PORT), authkey=b'lxx')
    proxy = RPCProxy(c)
    return proxy.release_session_lock(os.getpid())

_TF_NewGraph = TF_NewGraph
def TF_NewGraph_Proxy():
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    return _TF_NewGraph()
TF_NewGraph = TF_NewGraph_Proxy

_TF_SessionRunCallable = TF_SessionRunCallable
def TF_SessionRunCallable_proxy(session, handle, feed_values, run_metadata):
    return _TF_SessionRunCallable(session, handle, feed_values, run_metadata)
TF_SessionRunCallable = TF_SessionRunCallable_proxy

_TF_SessionRun_wrapper = TF_SessionRun_wrapper
def TF_SessionRun_wrapper_proxy(session, run_options, inputs, outputs, targets, run_metadata):
    acquire_session_lock()
    res =  _TF_SessionRun_wrapper(session, run_options, inputs, outputs, targets, run_metadata)
    release_session_lock()
    #print("TF_SessionRun_wrapper_proxy TF_GPUMemFree 0")
    #input()
    TF_GPUMemFree(session)
    #print("TF_SessionRun_wrapper_proxy TF_GPUMemFree 1")
    #input()
    return res
TF_SessionRun_wrapper = TF_SessionRun_wrapper_proxy


class RPCProxy:
    def __init__(self, connection):
        self._connection = connection
    def __getattr__(self, name):
        def do_rpc(*args, **kwargs):
            self._connection.send(pickle.dumps((name, args, kwargs)))
            result = pickle.loads(self._connection.recv())
            if isinstance(result, Exception):
                raise result
            return result
        return do_rpc