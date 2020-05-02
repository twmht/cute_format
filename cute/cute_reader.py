import os
import struct
import mmap
from multiprocessing import Process, Lock


class CuteReader():
    def __init__(self, path, use_mmap=False, order='<'):
        self.order = order
        path_to_index_db = os.path.join(path, 'index.db')
        self.path = path
        if not use_mmap:
            self.data_db = open(os.path.join(path, 'data.db'), 'rb')
            self.index_db = open(path_to_index_db, 'rb')
        else:
            with open(os.path.join(path, 'data.db'), 'rb') as f:
                self.data_db = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
            with open(path_to_index_db, 'rb') as f:
                self.index_db = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        self._num_data = int(os.stat(path_to_index_db).st_size / 12)
        self.lock = Lock()

    @property
    def num_data(self):
        return self._num_data

    def get(self, index):
        self.lock.acquire()
        index = index * 12
        self.index_db.seek(index)
        k, size = struct.unpack('{0}Qi'.format(self.order), self.index_db.read(12))
        self.data_db.seek(k)
        byte_object = struct.unpack('{0}{1}s'.format(self.order, size), self.data_db.read(size))[0]
        self.lock.release()
        return byte_object

    def __del__(self):
        self.close()

    def close(self):
        if self.data_db:
            self.data_db.close()
            self.data_db = None
        if self.index_db:
            self.index_db.close()
            self.index_db = None
