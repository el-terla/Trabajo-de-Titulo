import numpy as np
from scipy.constants import g
mm = 0.001 # m

#Parametros Bomba
Ds = 70 * mm # Diámetro Eje
D1 = 174.5 * mm # Diámetro sello frontal
D2 = 180 * mm # Diámetro sello trasero
De = 163.4 * mm # Diámetro entrada
Di = 336 * mm # Diámetro impulsor
deq = 1/100 # Desequilibrio en impulsor (1% por regla, 0.1% por medicion, 0.01% por norma)
Mi = 18 # kg Masa Impulsor
doble_voluta = True
B = 42 * mm # Espesor Impulsor
Q_h = 200 #m3/h # Caudal de operación
H = 173 #m
Q_bep = 450 # Caudal de mayor eficiencia
RPM = 3000
rho = 1000 #kg/m3
#fin parametros

kgf = lambda N: round(N/g, 1)
A = lambda d: d**2 * np.pi / 4
Q = Q_h / 3600 #m3/s
omega = 2*np.pi*RPM/60
As = A(Ds)
PI = 98e3 # Pa
PD = H * 9.81 * rho
PA = 101.3e3 #Pa
PC = 333e3 #Pa
A1 = A(D1)
A2 = A(D2)
F1 = PI * A1
F2 = PD * (A2 - A1)
F3 = PC * (A2 - As)
F4 = PA * As
F5 = rho * Q**2 / (A(De) - As)
FA = (F3 + F4) - (F1 + F2 + F5)
print(f"Fuerza axial neta: {FA} N = {kgf(FA)} kgf")
print(f"Componente entrada: {F1} N = {kgf(F1)} kgf")
print(f"Componente sin compensar: {F2} N = {kgf(F2)} kgf")
print(f"Componente caja compensación: {F3} N = {kgf(F3)} kgf")
print(f"Componente atmosférica: {F4} N = {kgf(F4)} kgf")
print(f"Componente inercial: {F5} N = {kgf(F5)} kgf\n")
K = 0.36 * (1 - (Q_h/Q_bep)**2)
P = K * rho * g * H * Di * B
print(kgf(P))
if doble_voluta:
    P = 0.4 * P
F_c = deq * Mi * (Di/2) * (RPM * 2 * np.pi / 60) ** 2
F_R = P + F_c
print(f"Fuerza radial: {P} N = {kgf(P)} kgf")
print(f"Fuerza centrífuga: {F_c} N = {kgf(F_c)} kgf")
print(f"Total de fuerzas radiales: {F_R} N = {kgf(F_R)} kgf\n")
eje = [348, 450]
T = (sum(eje) * mm) * F_R
F_rod_inf = T/(eje[0] * mm)
F_rod_sup = abs(F_R - F_rod_inf)
print(f"Fuerzas radiales sobre rodamientos:")
print(f"Par de rodamiento superior: {kgf(F_rod_sup)} kgf ({kgf(F_rod_sup/2)} cada uno)")
print(f"Rodamiento inferior: {kgf(F_rod_inf)} kgf\n")
print(f"Fuerza axial: {kgf(FA)} kgf, totalmente sobre 1 de los rodamientos superiores")