import tornado.ioloop
import tornado.web
import argparse
import sys, os, subprocess, time

# _posts文件夹
folder_posts = ""

def getFormatTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getPostList():
    result = {
        'dir': [],
        'file': []
    }
    for f in os.listdir(folder_posts):
        if os.path.isdir(f):
            result['dir'].append(f)
        if os.path.isfile(f):
            result['file'].append(f)
    return result

class Commands:

    @classmethod
    def execute(cls, command):
        res = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res.wait(10)
        result = {
            'code': 1,
            'error': ''
        }
        s = res.stderr.read()
        if s != "":
            result['code'] = 0
            result['error'] = s.decode('gbk')
        return result

    @classmethod
    def new_post(cls, fname):
        res = cls.execute("hexo new post {fname}".format(fname=fname))
        if res['code'] == 1:
            res['filepath'] = os.path.join(folder_posts, fname+'.md')
        return res

    @classmethod
    def deploy(cls):
        return "hexo d"

    @classmethod
    def generate(cls):
        return "hexo g"

    @classmethod
    def deploy_generate(cls):
        return "hexo d -g"

class NewPost(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        fname = self.get_argument('filname', default=getFormatTime())
        res = Commands.new_post(fname)
        if res['code'] == 1:
            fpath = res['filepath']
            with open(fpath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.write(data)
            # # 记得有finish哦
            self.finish()

class Deploy(tornado.web.RequestHandler):
    def post(self, *args, **kargs):
        pass

class Generate(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        pass

class GetAll():
    def get(self, *args, **kwargs):
        pass

class BackUp():
    def post(self, *args, **kwargs):
        pass

class UpLoadMd(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        files = self.request.files
        for file in files:


def make_app():
    return tornado.web.Application([
        (r"newpost/", NewPost),
        (r"deploy/", Deploy),
        (r"generate/", Generate),
        (r"getall/", GetAll),
        (r"backup/", BackUp),
        (r"upload/", UpLoad),
    ])

def getArg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8888, type=int)
    return parser.parse_args()

if __name__ == "__main__":
    args = getArg()
    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()