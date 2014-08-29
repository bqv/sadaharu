# number.py: A quaternion number

from hooks import Hook
import traceback
import cmath
import math

class Quaternion():
    def __init__(self, x=0, i=0, j=0, k=0):
        self.x = float(x);
        self.i = float(i);
        self.j = float(j);
        self.k = float(k);

    def __repr__(self):
        s = ""
        if self.x != 0:
            s += "%g"%(self.x,)
        if self.i != 0:
            if self.i == 1: s += "+i"
            elif self.i == -1: s += "-i"
            else: s += "+%gi"%(self.i,)
        if self.j != 0:
            if self.j == 1: s += "+j"
            elif self.j == -1: s += "-j"
            else: s += "+%gj"%(self.j,)
        if self.k != 0:
            if self.k == 1: s += "+k"
            elif self.k == -1: s += "-k"
            else: s += "+%gk"%(self.k,)
        if len(s) == 0:
            return "0"
        else:
            return s.replace("+-", '-').strip("+")

    def __add__(self, other):
        return Quaternion(self.x+other.x,self.i+other.i,self.j+other.j,self.k+other.k)

    def __mul__(self, other):
        #(a,b,c,d)(e,f,g,h) = (ae-bf-cg-dh,af+be+ch-dg,ag-bh+ce+df,ah+bg-cf+de)
        return Quaternion(self.x*other.x-self.i*other.i-self.j*other.j-self.k*other.k,self.x*other.i+self.i*other.x+self.j*other.k-self.k*other.j,self.x*other.j-self.i*other.k+self.j*other.x+self.k*other.i,self.x*other.k+self.i*other.j-self.j*other.i+self.k*other.x)
    def __conj__(self):
        return Quaternion(self.x,-self.i,-self.j,-self.k)
    def __norm__(self):
        return Quaternion(((self.x**2)+(self.i**2)+(self.j**2)+(self.k**2))**0.5,0,0,0)
    def __invert__(self):
        c = Quaternion(self.x,-self.i,-self.j,-self.k)
        n = 1/((self.x**2)+(self.i**2)+(self.j**2)+(self.k**2))
        return c*Quaternion(n,0,0,0)
    def __exp__(self):
        try:
            r = math.exp(self.x)
        except OverflowError:
            r = float("inf")
        mv = ((self.i**2)+(self.j**2)+(self.k**2))**0.5
        if mv == 0:
            return Quaternion(r,0,0,0)
        else:
            x = math.cos(mv)
            s = math.sin(mv)
            i = s*(self.i/mv)
            j = s*(self.j/mv)
            k = s*(self.k/mv)
            return Quaternion(r*x,r*i,r*j,r*k)
    def __log__(self):
        mv = ((self.i**2)+(self.j**2)+(self.k**2))**0.5
        mq = ((self.x**2)+(mv**2))**0.5
        if mq == 0:
            return Quaternion(float("-inf"),float("-inf"),float("-inf"),float("-inf"))
        x = math.log(mq)
        if mv == 0:
            return Quaternion(x,0,0,0)    
        else:
            a = math.acos(self.x/mq)
            i = a*(self.i/mv)
            j = a*(self.j/mv)
            k = a*(self.k/mv)
            return Quaternion(x,i,j,k)
    def __sqrt__(self):
        mv = ((self.i**2)+(self.j**2)+(self.k**2))**0.5
        mq = ((self.x**2)+(mv**2))**0.5
        if mv == 0:
            c = complex(cmath.sqrt(self.x))
            return Quaternion(c.real,c.imag,0,0)    
        else:
            x = math.sqrt((mq+self.x)/2)
            v = math.sqrt((mq-self.x)/2)
            i = v*(self.i/mv)
            j = v*(self.j/mv)
            k = v*(self.k/mv)
            return Quaternion(x,i,j,k)

def getnum(bot):
    return bot.data.get("number", Quaternion())

def saynum(bot, dest):
    bot.privmsg(dest, "The number is now %s" %(bot.data['number'],))

@Hook('COMMAND', commands=["inc",])
def add(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(1,0,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["iinc",])
def iadd(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,1,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["jinc",])
def jadd(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,0,1,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["kink",])
def kadd(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,0,0,1)
    saynum(bot,ev.dest)
    return ev

@Hook('COMMAND', commands=["sub",])
def subtract(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(-1,0,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["isub",])
def isubtract(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,-1,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["jsub",])
def jsubtract(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,0,-1,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["ksub",])
def ksubtract(bot, ev):
    bot.data['number'] = getnum(bot)+Quaternion(0,0,0,-1)
    saynum(bot,ev.dest)
    return ev

@Hook('COMMAND', commands=["mul",])
def multiply(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(2,0,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["imul",])
def imultiply(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,2,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["jmul",])
def jmultiply(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,0,2,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["kmul",])
def kmultiply(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,0,0,2)
    saynum(bot,ev.dest)
    return ev

@Hook('COMMAND', commands=["div",])
def divide(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(2,0,0,0).__invert__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["idiv",])
def idivide(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,2,0,0).__invert__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["jdiv",])
def jdivide(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,0,2,0).__invert__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["kdiv",])
def kdivide(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(0,0,0,2).__invert__()
    saynum(bot,ev.dest)
    return ev

@Hook('COMMAND', commands=["neg",])
def negate(bot, ev):
    bot.data['number'] = getnum(bot)*Quaternion(-1,0,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=[])
def square(bot, ev):
    bot.data['number'] = getnum(bot)*getnum(bot)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["num",])
def number(bot, ev):
    getnum(bot)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["diff",])
def differentiate(bot, ev):
    bot.data['number'] = Quaternion(0,0,0,0)
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["conj",])
def conjugate(bot, ev):
    bot.data['number'] = getnum(bot).__conj__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["norm",])
def normalize(bot, ev):
    bot.data['number'] = getnum(bot).__norm__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["inv",])
def invert(bot, ev):
    bot.data['number'] = getnum(bot).__invert__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["exp",])
def exponentiate(bot, ev):
    bot.data['number'] = getnum(bot).__exp__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["log",])
def logarithm(bot, ev):
    bot.data['number'] = getnum(bot).__log__()
    saynum(bot,ev.dest)
    return ev
@Hook('COMMAND', commands=["sqrt","root"])
def squareroot(bot, ev):
    bot.data['number'] = getnum(bot).__sqrt__()
    saynum(bot,ev.dest)
    return ev
