import math


#calculates the discretization correction factor
def discr_corr(l,r):
    '''
    Returns the discretization correction factor for Lamda = l and band exponent r.
    args: l-->float, r-->float
    returns: correction_factor: float
    '''
    A=((1-l**(-(2+r)))/(2+r))**(1+r)
    B=((1+r)/(1-l**(-(1+r))))**(2+r)
    C=math.log(l)
    return A*B*C