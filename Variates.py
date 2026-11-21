import sys
import math

# Truncated Exponential Variate function using the method of constrained inversion
def trunc_Exponential(mu, a, b, trace):
    alpha = cdf_Exponential(mu, a)
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
# Helper function for Exponential cdf
def cdf_Exponential(mu, x):
    return 1-math.exp(-x/mu)
# Helper function for Exponential idf
def idf_Exponential(mu, u):
    return -mu*math.log(1-u)
# Helper function for Uniform idf
def Uniform(a, b, u):
    return a + (b - a) * u
    
# Truncated Geometric Variate function using the method of CDF modification and search
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
# Helper function for Geometric cdf
def cdf_Geometric(p, x):
    return 1 - p**(x+1)
# Helper function for truncated Geometric cdf
def trunc_cdf_Geometric(p, x, a, b):
    return (cdf_Geometric(p, x) - cdf_Geometric(p, a-1)) / (cdf_Geometric(p, b) - cdf_Geometric(p, a-1))      

# Equilikely Random Variate function for use in destination floor allocation
def Equilikely(a, b, trace):
    try:
        u_val = trace.readline()
        if not u_val: raise ValueError("EOF reached")
        u = float(u_val)
    except ValueError:
        # print(f"Error: Could not convert string to float or EOF reached.")
        sys.exit(1)
    return (a+(int)((b-a+1)*u))