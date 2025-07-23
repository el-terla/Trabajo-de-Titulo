from numpy import exp, sqrt, log10, pi
from scipy.optimize import curve_fit


# Parámetros de entrada
T_amb = 30 #°C
Fr = 22e3 #N
R1 = 1.09e-6 # 1.09e-6 para 218 y 1.4e-6 para 2218

n = 2980 #RPM

#Fin Parámetros

D = 160 #mm
d = 90 #mm
Fa = 0 #N



S1 = 0.16
S2 = 0.0015

nu_40 = 110 #mm2/s
nu_100 = 10 #mm2/s

Krs = 6e-8
KZ = 5.1

Ws=9.5 #9.5 para 218 y  10.5 para 2218

Nu = lambda t, A, B: 10**(10**(A - B * log10(t))) - 10.8
dm = (d + D) / 2

A,B = curve_fit(f=Nu, xdata=[40, 100], ydata=[nu_40, nu_100])[0]

t = T_amb + 20
t_old = T_amb

while abs(t-t_old) >= 0.1:
    nu = Nu(t, A, B)

    Phish = 1/(1 + 1.84e-9 * (n * dm)**1.28 * (nu**0.64))

    Phirs = 1/exp(Krs * nu * n * (d + D) * sqrt(KZ/(2 * (D - d))))

    G_rr = R1 * (dm ** 2.41) * (Fr**0.31)
    M_rr = Phish * Phirs * G_rr * ((nu * n) ** 0.6)

    Phibl = 1 / exp(2.6e-8 * ((n * nu)**1.4 ) * dm)
    mu_bl = 0.12
    mu_EHL = 0.02
    mu_sl = Phibl * mu_bl + (1 - Phibl) * mu_EHL

    G_sl = S1 * (dm ** 0.9) * Fa + (S2 * dm * Fr)
    M_sl = G_sl * mu_sl

    M_seal = 0
    M_drag = 0

    M = M_rr + M_sl + M_seal + M_drag

    NR = 2 * pi * M * n * 1e-3 / 60

    dT = NR/Ws
    t_old = t
    t = T_amb + dT

print(f"Viscocidad: {round(nu, 2)} mm/s^2")
print(f"Potencia disipada: {round(NR,1)} W")
print(f"Momento de roce es: {round(M,1)} Nmm")
print(f"rodar: {round(M_rr,1)} Nmm, deslizar: {round(M_sl)} Nmm")
print(f"Temperatura de operación: {t}°C")
