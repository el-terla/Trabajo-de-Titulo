import pycba as cba
from numpy import pi, array, linspace, rad2deg, arctan
#from matplotlib import pyplot as plt
from math import ceil
from scipy.optimize import minimize

# --- Utilidades ---
mm = 1e-3
I = lambda d: pi * d**4 / 64  # Momento de inercia circular

def multiply_nested_list(data, factor):
    """Multiplica recursivamente los elementos de una lista anidada."""
    if isinstance(data, list):
        return [multiply_nested_list(item, factor) for item in data]
    return data * factor

def clean_data(X, Y):
    """Filtra puntos donde la pendiente es excesiva o X no cambia."""
    OUTX, OUTY = [], []
    for i in range(len(X) - 1):
        x1, x2 = X[i], X[i + 1]
        y1, y2 = Y[i], Y[i + 1]
        if x1 != x2:
            m = (y2 - y1) / (x2 - x1)
            if abs(m) < 1000:
                OUTX.append(x1)
                OUTY.append(y1)
    return OUTX, OUTY


# ##### PARAMETROS #####


E = 200e9  # Módulo de Young [Pa]
res = 4 * mm  # Resolución de discretización en secciones cónicas

#  #### FIN PARAMETROS ####
DR = 90 #diámetro interno rodamiento inferior
def calcular_eje(x):
    var, D1, D2, F = x
    #name="Eje Nuevo opti",
    apoyos=[0, 4]
    Eje=[
        [55, 21],
        [70, 119],
        [70, 17.32, DR],
        [DR, var],
        [DR, 15],
        [102, 6],
        [102, 4.33, D1],
        [D1, 144.51],
        [D1, 60.16, D2],
        [D2, 161.1],
        [D2, 28.5, 53],
        [45, 30]
    ]

    Eje = multiply_nested_list(Eje, mm)
    #Largo = sum(seg[1] for seg in Eje)

    # Posiciones de rodamientos
    D_rod = [Eje[a][0] for a in apoyos]
    X_rod = [sum(seg[1] for seg in Eje[:a]) for a in apoyos]

    D = []
    L = []
    desface_nodo = [0 for _ in apoyos]

    # Descomposición del eje en segmentos uniformes o cónicos
    for i, seg in enumerate(Eje):
        if len(seg) == 2 or seg[1] < res:
            D.append(seg[0])
            L.append(seg[1])
        elif len(seg) == 3:
            d0, l, df = seg
            steps = round(l / res)
            d = linspace(d0, df, steps + 1)
            d = d[1:] if d0 >= df else d[:-1]
            D += list(d)
            L += [l / steps] * steps
            for a in range(len(apoyos)):
                if i < apoyos[a]:
                    desface_nodo[a] += steps - 1
        else:
            raise ValueError("Error en formato de las medidas del eje.")



    # Geometría ideal
    X, Y, x = [], [], 0
    for seg in Eje:
        X.append(x)
        Y.append(seg[0])
        if len(seg) == 3:
            Y.append(seg[2])
        else:
            Y.append(seg[0])
        x += seg[1]
        X.append(x)

    # Geometría simulada
    X, Y = [], []
    for i in range(len(D)):
        x0 = sum(L[:i])
        xf = x0 + L[i]
        X += [x0, xf]
        Y += [D[i]] * 2


    # --- Simulación de deflexión con pycba ---
    EI = [E * I(d) for d in D]
    R = [0] * ((len(L) + 1) * 2)
    for i, a in enumerate(apoyos):
        R[(a + desface_nodo[i]) * 2] = -1

    beam_analysis = cba.BeamAnalysis(L, EI, R)
    beam_analysis.add_pl(len(L), -F, L[-1])
    beam_analysis.analyze()
    results = beam_analysis._beam_results.results
    reacciones = beam_analysis.beam_results.R
    rotaciones = []
    for X in X_rod:
        n1 = min(range(len(results.x)), key=lambda i: abs(results.x[i] - (X - 2 * mm)))
        n2 = min(range(len(results.x)), key=lambda i: abs(results.x[i] - (X + 2 * mm)))
        m = (results.D[n2] - results.D[n1]) / (results.x[n2] - results.x[n1])
        rotaciones.append(rad2deg(arctan(m)))

    # --- Gráfica de la deflexión ---
    X, Y = clean_data(results.x, results.D / mm)

    # Texto con flechas máximas
    x_crit = sum([seg[1] for seg in Eje[0:-2]])
    i_crit = min(range(len(Y)), key=lambda i: abs(X[i] - x_crit))
    d_crit = Y[i_crit]

    #print(f"Flecha máxima: {round(Y[-1], 3)} mm, Flecha crítica: {round(d_crit, 3)} mm")
    #print(f"Reacción Superior: {round(reacciones[0])} N, Reacción Inferior: {round(reacciones[1])} N")
    #print(f"Angulo Superior: {round(rotaciones[0], 4)}°, Angulo Inferior: {round(rotaciones[1], 4)}°")
    #print()

    return -F, abs(reacciones[1]), abs(reacciones[0]), d_crit

def objetivo(x):
    d_crit = calcular_eje(x)[0]
    return d_crit

R1_max = 22e3
def restriccion_R1(x):
    reaccion = calcular_eje(x)[1]
    return R1_max - reaccion

R2_max = 9.6e3
def restriccion_R2(x):
    reaccion = calcular_eje(x)[2]
    return R2_max - reaccion

D_max = 0.430 #en micras
def restriccion_flecha(x):
    d_crit = calcular_eje(x)[3]
    return (D_max - d_crit)/mm




if __name__ == "__main__":

    separacion_min = 50
    separacion_max = 300

    D_mayor_min = 102
    D_mayor_max = 106

    D_buje_min = 60
    D_buje_max = 70

    F_min = 4000
    F_max = 8000


    restricciones = [
        {"type": "ineq", "fun": restriccion_R1},
        {"type": "ineq", "fun": restriccion_R2},
        {"type": "ineq", "fun": restriccion_flecha}]

    bounds = [(separacion_min, separacion_max),
              (D_mayor_min, D_mayor_max),
              (D_buje_min, D_buje_max),
              (F_min, F_max)]

    x0 = array([150, 105, 65, 6814])
    result = minimize(objetivo, x0=x0, method="COBYLA", bounds=bounds, constraints=restricciones, tol=0.1)
    print(result.x)
    print(result.fun)
    print(f"Flecha: {round(D_max - restriccion_flecha(result.x)*mm, 3)} mm")
    print(f"Reaccion Inferior: {round(R1_max - restriccion_R1(result.x))} N")
    print(f"Reaccion Superior: {round(R2_max - restriccion_R2(result.x))} N")
