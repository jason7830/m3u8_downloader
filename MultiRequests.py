import threading
import multiprocessing as mp
import queue
import requests
class Requester():
    def __init__(self,requests,threads=1):
        self.requests = requests
        self.threads = threads
        self.pool = mp.Pool(processes=threads)
    
    def run(self,request):
        request.download()
    
    def run_map(self):
        return self.pool.map_async(self.run,self.requests)

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


class request():
    def __init__(self,url,save_path,headers=None,delay=0,verbose=None):
        self.url = url
        self.save_path = save_path
        self.verbose = verbose
        self.headers = headers
        self.verbose = verbose
        

    def getHEAD(self):
        with requests.get(url,headers=self.headers,stream=True) as r:
            return r.headers


    def download(self):
        with requests.get(self.url, allow_redirects=True, headers=self.headers, stream=True) as r:
            content_len = r.headers['Content-Length']
            with open(self.save_path,'wb') as f:
                #chunk size = 50kb
                chunk_size=51200
                for i,chunck in enumerate(r.iter_content(chunk_size=chunk_size)):
                    if chunck:
                        f.write(chunck)
                        if self.verbose is not None:
                            self.verbose['bytes'] += len(chunck)
                """if self.verbose is not None:
                    self.verbose['done'] += '{} -- downloaded! ({}/{}) bytes     \n'.format(self.save_path,content_len,content_len)
                    self.verbose.pop(self.save_path)
                    """
                