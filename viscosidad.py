from numpy import exp, sqrt, log10, pi
from scipy.optimize import curve_fit

nus = [110, 63.6, 39.6, 26.2, 18.2, 13.2, 10]
Ts = [40, 50, 60, 70, 80, 90, 100]
T = 70
Nu = lambda t, A, B, l: 10**(10**(A - B * log10(t))) - l
A,B,l = curve_fit(f=Nu, xdata=Ts, ydata=nus)[0]
nu = Nu(T, A, B, l)
print(nu)