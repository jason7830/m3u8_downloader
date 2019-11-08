import m3u8
import os
from queue import Queue,Empty
from multiprocessing import Manager
from MultiRequests import Requester, request
import subprocess as sp
from threading import Thread
import re
class Downloader():
    def __init__(self,m3u8_path,save_name,threads=1,show_verbose=True):
        self.seg_queue = Queue()
        self.seg_list = []
        self.save_name = re.sub('[/\\:?\*"<>|]','',save_name)[:200]
        self.m3u8_path = m3u8_path
        self.seg_num = 0
        self.seg_name = m3u8_path.split('/')[-1][:-5]
        self.seg_verbose = Manager().dict()
        self.seg_verbose['bytes'] = 0
        self.threads = threads
        self.show_verbose = show_verbose
        for i,s in enumerate(m3u8.load(m3u8_path).segments):
            seg = '{}/{}-seg-{}.ts'.format('segments',self.seg_name,i+1)
            #self.seg_verbose[seg] = ''
            self.seg_num += 1
            #self.seg_queue.put(request(s.uri,seg))
            self.seg_list.append(request(s.uri,seg,verbose=self.seg_verbose))
        self.requester = Requester(self.seg_list,threads=threads)

    def file_size_transfer(self,bytes):
        if bytes >= 1048576:
            return [bytes/1048576,'mb']
        if bytes >= 1024:
            return [bytes/1024,'kb']
        return [bytes,'bytes']


    def download(self,verbose=True):
        result = self.requester.run_map()
        while True:
            try:
                result.successful()
                break
            except Exception as e:
                if verbose:
                    downloaded_size = self.file_size_transfer(self.seg_verbose['bytes'])
                    print('{}... -- downloading ({:.2f}) {}          '.format(self.save_name[:15],downloaded_size[0],downloaded_size[1]),end='\r')
        print("{} Complete!".format(self.m3u8_path))

    def getabit(self,o,q):
        for c in iter(lambda:o.read(1),b''):
            q.put(c)
        print('PIPE CLOSED')
        o.close()

    def getdata(self,q):
        r = b''
        while True:
            try:
                c = q.get(False)
                if c.decode() == '\n':
                    r+=c
                    break
            except Empty:
                return None
            else:
                r += c
        return r

    def concatSegs(self,remove_segs=False):
        segs_files = []
        arg_files = '"concat:'
        import csv
        tmp = []
        for i,l in enumerate(os.listdir('segments')):
            if self.seg_name in l:
                tmp.append(["file 'segments/{}'".format(l)])
                segs_files.append('segments/'+l)
                arg_files += 'segments/'+l+'|'
        arg_files = arg_files[:-1] + '"'
        tmp.sort(key=lambda x:int(x[0].split('-')[-1][:-4]))
        with open('tmp.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerows(tmp)
        arg = 'ffmpeg -y -f concat -i tmp.csv -c copy "tmp.mp4"'
        #arg = 'ffmpeg -y -i {} -c copy {}'.format(arg_files,self.save_name)
        print(arg)
        pobj = sp.Popen(arg,stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.STDOUT,shell=True)
        q = Queue()
        t = Thread(target=self.getabit,args=(pobj.stdout,q))
        t.daemon = True
        t.start()
        s =""
        while True:
            try:
                tmp = self.getdata(q)
                if tmp is not None:
                    s = tmp.decode()
            except UnicodeDecodeError:
                print("UnicodeDecodeError...")
            print(s,end='\r')
            if (not t.isAlive()) and tmp is None:
                break
        if 'muxing overhead' in s:
            print('[{}...] merging successful!'.format(self.save_name[:10]))
            os.rename('tmp.mp4',self.save_name)
            if remove_segs:
                for seg in segs_files:
                    os.remove(seg)