import sys
import math

def trunc_Exponential(mu, a, b, trace):
    alpha = cdf_Exponential(mu, a-1)
    beta = 1 - cdf_Exponential(mu, b)
    try:
        u_val = trace.readline()
        if not u_val: raise ValueError("EOF reached")
        u_val = float(u_val)
    except ValueError:
        # print(f"Error: Could not convert string to float or EOF reached.")
        sys.exit(1)
    u = Uniform(alpha, 1.0-beta, u_val)
    return idf_Exponential(mu, u)

def cdf_Exponential(mu, x):
    return 1-math.exp(-x/mu)
def idf_Exponential(mu, u):
    return -mu*math.log(1-u)
def Uniform(a, b, u):
    return a + (b - a) * u
    
    
def trunc_Geometric(p, a, b, trace):
    try:
        u_val = trace.readline()
        if not u_val: raise ValueError("EOF reached")
        u = float(u_val)
    except ValueError:
        # print(f"Error: Could not convert string to float or EOF reached.")
        sys.exit(1)
    d = (a+b)//2
    if (trunc_cdf_Geometric(p, d, a, b) <= u):
        while (trunc_cdf_Geometric(p, d, a, b) <= u): d += 1
    elif (trunc_cdf_Geometric(p, a, a, b) <= u):
        while (trunc_cdf_Geometric(p, d-1, a, b) > u): d -= 1
    else: d = a
    return d
    
def cdf_Geometric(p, x):
    return 1 - p**(x+1)
def trunc_cdf_Geometric(p, x, a, b):
    return (cdf_Geometric(p, x) - cdf_Geometric(p, a-1)) / (cdf_Geometric(p, b) - cdf_Geometric(p, a-1))      


def Equilikely(a, b, trace):
    try:
        u_val = trace.readline()
        if not u_val: raise ValueError("EOF reached")
        u = float(u_val)
    except ValueError:
        # print(f"Error: Could not convert string to float or EOF reached.")
        sys.exit(1)
    return (a+(int)((b-a+1)*u))

def variate_test(tfile):
    try:
        trace = open(tfile, 'r')
    except FileNotFoundError:
        # print(f"Error: The trace file at {tfile} was not found.")
        sys.exit(1)

    b = [trunc_Geometric(0.65, 1, 8, trace) for _ in range(10_0000)]
    d = [0]*8
    for i in b: d[i-1] += 1
    print(*d)