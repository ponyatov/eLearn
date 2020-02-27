
import os,sys

########################################### Marvin Minsky's extended frame model

class Frame:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.val  = V
        self.slot = {}
        self.nest = []

    ################################### dump

    def __repr__(self):
        return self.dump()
    def dump(self,depth=0,prefix=''):
        tree = self.pad(depth) + self.head(prefix)
        if not depth: Frame.dumped = []
        if self in Frame.dumped: return tree + ' _/'
        else: Frame.dumped.append(self)
        for i in self.slot:
            tree += self.slot[i].dump(depth+1, prefix = '%s = ' % i)
        idx = 0
        for j in self.nest:
            tree += j.dump(depth+1, prefix='%s = ' % idx) ; idx += 1
        return tree
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def pad(self,depth):
        return '\n' + '\t' * depth
    def _val(self): return str(self.val)

    ############################## operators

    def __getitem__(self,key):
        return self.slot[key]
    def __setitem__(self,key,that):
        if callable(that): return self.__setitem__(key,Cmd(that))
        self.slot[key] = that ; return self
    def __lshift__(self,that):
        return self.__setitem__(that.type,that)
    def __rshift__(self,that):
        if callable(that): return self.__rshift__(Cmd(that))
        return self.__setitem__(that.val,that)
    def __floordiv__(self,that):
        self.nest.append(that) ; return self

    ############################## stack ops

    def pop(self): return self.nest.pop()
    def top(self): return self.nest[-1]
    def dot(self): self.nest = [] ; return self


################################################################ primitive types

class Primitive(Frame):
    def eval(self,env): return env // self

class Symbol(Primitive): pass
class String(Primitive): pass
class Number(Primitive): pass
class Integer(Number): pass

################################################ EDS: executable data structures

class Active(Frame): pass

class Cmd(Active):
    def __init__(self,F):
        Active.__init__(self,F.__name__)
        self.fn = F
    def eval(self,env):
        self.fn(env)

class VM(Active): pass

############################################################# global environment

vm = VM('metaL') ; vm << vm

########################################################################## debug

def BYE(env): sys.exit(0)

def Q(env): print(env)
vm['?'] = Q

def QQ(env): print(env) ; BYE(env)
vm['??'] = QQ

################################################################## manipulations

def EQ(env): addr = env.pop().val ; env[addr] = env.pop()
vm['='] = EQ

def PUSH(env): that = env.pop() ; env.top() // that
vm['//'] = PUSH

def DOT(env): env.dot()
vm['.'] = DOT

############################################################################ I/O

class IO(Frame): pass

######################################################################## Network

class Net(IO): pass
class IP(Net):
    def eval(self,env): return env // self

########################################################## PLY: no-syntax parser

import ply.lex as lex

tokens = ['symbol','string','number','integer','ip']

t_ignore         = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

def t_ip(t):
    r'([0-9]{1,3}\.){3}[0-9]{1,3}'
    return IP(t.value)

def t_number(t):
    r'[+\-]?[0-9]+\.[0-9]*'
    return Number(t.value)

def t_integer(t):
    r'[+\-]?[0-9]+'
    return Integer(t.value)

def t_symbol(t):
    r'[`]|[^ \t\r\n\#\\]+'
    return Symbol(t.value)

def t_ANY_error(t): raise SyntaxError(t)

lexer = lex.lex()

#################################################################### interpreter

def WORD(env):
    token = lexer.token()
    if token: env // token
    return token
vm['`'] = WORD

def FIND(env):
    token = env.pop()
    try: env // env[token.val] ; return True
    except KeyError: env // token ; return False

def EVAL(env): env.pop().eval(env)

def INTERP(env):
    lexer.input(env.pop().val)
    while True:
        if not WORD(env): break
        if isinstance(env.top(),Symbol):
            if not FIND(env): raise SyntaxError(env.top())
        EVAL(env)
    print(env)


################################################################## Web interface

class Web(Net):
    def eval(self,env):
        print(env)
        from flask import Flask,Response,render_template
        app = Flask(self.val)

        @app.route('/')
        def index(): return render_template('index.html',env=env)

        @app.route('/css.css')
        def css(): return Response(render_template('css.css',env=env),mimetype='text/css')

        @app.route('/logo.png')
        def logo(): return app.send_static_file('logo.png')

        app.run(host=env['IP'].val, port=env['PORT'].val, debug=True, extra_files=sys.argv[1])

vm['WEB'] = Web(vm.head())

class Color(Web): pass
class Font(Web): pass
class Size(Web): pass

def mm(env): env // Size('%smm' % env.pop().val)
vm >> mm


#################################################################### system init

if __name__ == '__main__':
    print(vm)
    for infile in sys.argv[1:]:
        with open(infile) as src:
            vm // String(src.read()) ; INTERP(vm)
