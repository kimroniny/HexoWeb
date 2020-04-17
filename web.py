# -*- coding: utf-8 -*-
import argparse
import sys, os
import traceback
import datetime
import time
import codecs
import json, random, re
from mylogger import Logger
from commands import Command as cmds

import tornado
import tornado.httpserver, tornado.ioloop, tornado.options
import tornado.httpclient, tornado.web, tornado.gen
import platform

logger = Logger(filename=__file__, maxBytes=10*1024*1024, backupCount=100)

def try_json_loads(body):
    try:
        res = json.loads(body)
    except Exception as e:
        print(traceback.format_exc())
        res = {}
    finally:
        return res

def fix_filename(filename):
    if isinstance(filename, bytes):
        filename = filename.decode()
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    filename = re.sub(rstr, "-", str(filename))
    return filename


def format_msg(code, out, err):
    return "{split}\ncode: \n{code}\n{split}\nout: \n{out}\n{split}\nerr: \n{err}\n{split}\n".format(
        code=code,
        out=out,
        err=err,
        split='-'*20
    ).encode('utf-8')


class audio_class_detect(tornado.web.RequestHandler):

    def initialize(self, args):
        """
        每次有请求过来，都会运行该函数
        """
        self.path_hexo = args.hd
        self.path_post = os.path.join(self.path_hexo, 'source', '_posts')
        logger.info("path of hexo: {}".format(self.path_hexo))
        logger.info("path of post: {}".format(self.path_post))

    def get(self, *args, **kwargs):
        logger.info("query_argument: {}".format(self.request.query_arguments))
        logger.info("body_arguments: {}".format(self.request.body_arguments))
        logger.info("arguments: {}".format(self.request.arguments))
        type = self.get_query_argument('type', None)
        if type == 'download':
            self.__cmd_download()
        else:
            self.write("unknown type")

    def post(self, *args, **kwargs):
        try:
            code, out, err = self.__parse_args()
            self.write(format_msg(code, out, err))
        except Exception as e:
            logger.error(traceback.format_exc())
            self.write("fail, err: {}".format(str(e)))


    def __parse_args(self):
        '''
        type: [
            n_p: new post, 
            g: generate, 
            d: deploy, 
            g_d: generate & deploy, 
            u: upload files, 
            p: push to branch-hexo
            help: show cmds,
            list: show files in _post,
        ]
        '''
        type = self.get_argument('type', default=None)
        logger.info("type: {}".format(type))
        if not type:
            code, out, err = -1, "", "type is None"
        elif type == 'n_p':
            code, out, err = self.__cmd_np()
        elif type == 'g':
            code, out, err = self.__cmd_generate()
        elif type == 'd':
            code, out, err = self.__cmd_deploy()
        elif type == 'g_d':
            code, out, err = self.__cmd_gd()
        elif type == 'u':
            code, out, err  = self.__cmd_upload()
        elif type == 'git_add':
            code, out, err = self.__cmd_git_add()
        elif type == 'git_commit':
            code, out, err = self.__cmd_git_commit()
        elif type == 'git_push':
            code, out, err = self.__cmd_git_push()
        elif type == 'help':
            code, out, err = self.__cmd_help()
        elif type == 'list':
            code, out, err = self.__cmd_list()
        elif type == 'rm':
            code, out, err = self.__cmd_del()
        else:
            code, out, err = -1, "", "未知参数"
        return code, out, err


    # new post
    def __cmd_np(self):
        fname = self.get_argument('filename', None)
        logger.info("filename: {}".format(fname))
        if fname:
            statement = "hexo new post \"{}\"".format(fname)
            res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
            return (-1 if res != 0 else res), out, err
        else:
            return -1, "", "filename can't be None"

    def __cmd_generate(self):
        statement = "hexo g"
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_deploy(self):
        statement = "hexo d"
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_gd(self):
        statement = "hexo g -d"
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_upload(self):
        res_md = self.__save_md()
        res_img = self.__save_img()
        result = {}
        if res_md[1] != "" and res_img[1] != "":
            return -1, "", "upload: {}, {}".format(res_md[1], res_img[1])
        if res_md[1] == "":
            result['save_md'] = res_md[0]
        if res_img[1] == "":
            result['save_img'] = res_img[0]
            result['save_img_dir'] = res_img[2]
        return 0, result, ""

    def __cmd_git_add(self):
        statement = "git add"
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_git_commit(self):
        msg = self.get_argument("commit_msg", None)
        if not msg:
            return -1, "", "commit msg can't be None"
        statement = "git commit -m '{}'".format(msg)
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_git_push(self):
        statement = "git push origin hexo"
        res, out, err = cmds.execute(statement=statement, cwd=self.path_hexo)
        return res, out, err

    def __cmd_list(self):
        statement = "ls -lht" # here we can not use 'll -ht', because bash or sh can not find command 'll' and 'll' is alias to 'ls' meaning 'ls -l' == 'll'
        res, out, err = cmds.execute(statement, cwd=self.path_post)
        return res, out, err

    def __cmd_del(self):
        filename = self.get_argument("filename", None)
        if filename is None:
            return -1, "", "filename to remove can not be None"
        statement = "rm -rf {}".format(filename)
        logger.info("execute statement: {}".format(statement))
        res, out, err = cmds.execute(statement=statement, cwd=self.path_post)
        return res, out, err

    def __cmd_download(self):
        filename = self.get_argument("filename", None)
        if filename is None:
            return -1, "", "filename to download can not be None"
        logger.info("download file: {}".format(filename))
        self.__download_md(filename)

    def __download_md(self, filename):
        try:
            # http头 浏览器自动识别为文件下载
            self.set_header('Content-Type', 'application/octet-stream')
            # 下载时显示的文件名称
            self.set_header('Content-Disposition', 'attachment; filename=%s' % filename.encode('utf-8')) # filename can not be Chinese. Otherwise, encoding error happens.
            filepath = os.path.join(self.path_post, filename)
            with codecs.open(filepath, 'r', encoding='utf-8') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.write(data)
            self.finish()
        except Exception:
            self.clear_header("Content-type")
            self.clear_header("Content-Disposition")
            msg = "when download {}, err occurs: {}".format(filename, traceback.format_exc())
            logger.error(msg)
            self.write(msg)

    # save markdown files(check suffix .md ) and create images directory
    def __save_md(self):
        files = self.request.files.get('file_md')
        result = []
        if files is None:
            return None, "param:file_md is None"
        for file in files:
            filename = file.get('filename')
            if isinstance(filename, bytes):
                filename = filename.decode()
            else:
                filename = str(filename)
            # only markdown files
            if not filename.endswith(".md"):
                return result, "filename has to end with '.md': {}".format(filename)
            # sub filename illegal characters to '-'
            filename = fix_filename(filename)
            body = file.get('body')
            filepath = os.path.join(self.path_post, filename)
            with open(filepath, 'wb') as f:
                f.write(body)
                filedir = "".join(filepath.split('.')[:-1])
                if not os.path.exists(filedir):
                    os.makedirs(filedir)
            result.append(filename)
        return result, ''

    # save img files to corresponding dir(param: img_dir_name)
    def __save_img(self):
        files = self.request.files.get('file_img')
        result = []
        if files is None:
            return result, "param:file_img is None"
        img_dir_name = self.get_argument('img_dir_name', None)
        if img_dir_name is None:
            return result, "param:img_dir_name is None"
        img_dir = os.path.join(self.path_post, img_dir_name)
        for img in files:
            filename = img.get('filename')
            body = img.get('body')
            img_path = os.path.join(img_dir, filename)
            with open(img_path,'wb') as f:
                f.write(body)
            result.append(filename)
        return result, "", img_dir

    def __cmd_help(self):
        help_text = 'None'
        with open("types", 'r', encoding='utf-8') as f:
            help_text = f.read()
        return 0, help_text, ''


# curl http://127.0.0.1:10051/hexo -X POST -F "file_md=@commands.py" -F "file_md=@mylogger.py" -F type=u
def make_app(args):
    return tornado.web.Application([
        (r"/hexo", audio_class_detect, dict(args=args)),
    ])

def getArg():
    parser = argparse.ArgumentParser(description='params for python')
    parser.add_argument('--port', type=int, default=10051)
    parser.add_argument('--hd', type=str, default=os.environ.get('HEXO_ROOT', None), help="hexo dir")
    parser.add_argument('--start_num', type=int, default=1)
    return parser.parse_args()

if __name__ == "__main__":

    args = getArg()
    if not args.hd:
        logger.error("args.hd cannot be None")
        sys.exit(1)
    try:
        app = make_app(args)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.bind(args.port)
        http_server.start(args.start_num)
        logger.info("start server.....")
        tornado.ioloop.IOLoop.instance().start()
        time.sleep(1)
    except Exception as e:
        logger.error (traceback.format_exc())

