import pycba as cba
from numpy import pi, linspace, rad2deg, arctan, sin, arange
from matplotlib import pyplot as plt
from math import ceil
from ejes import*
# --- Utilidades ---
mm = 1e-3
I = lambda d: pi * d**4 / 64  # Momento de inercia circular

def multiply_nested_list(data, factor):
    """Multiplica recursivamente los elementos de una lista anidada."""
    if isinstance(data, list):
        return [multiply_nested_list(item, factor) for item in data]
    return data * factor

def clean_data(X, Y):
    # Filtra puntos donde la pendiente es excesiva o X no cambia.
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

obj_eje = eje_optimizado_def# Selección de Eje


#  #### FIN PARAMETROS ####

# Declaraciones y unidades
name = obj_eje.nombre
Eje = obj_eje.Eje
apoyos = obj_eje.apoyos
F = obj_eje.F

Eje = multiply_nested_list(Eje, mm)
Largo = sum(seg[1] for seg in Eje)

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

# --- Gráfica de la geometría ---
fig, (ax1, ax2) = plt.subplots(2, sharex=True)

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
ax1.plot(X, Y, "--", c="RED", label="Geometría del Eje")

# Geometría simulada
X, Y = [], []
for i in range(len(D)):
    x0 = sum(L[:i])
    xf = x0 + L[i]
    X += [x0, xf]
    Y += [D[i]] * 2
ax1.plot(X, Y, label="Geometría simulada")
ax1.set_aspect(1)

# Apoyos
for i, x in enumerate(X_rod):
    ax1.plot([x, x], [0, D_rod[i]], c="RED", linewidth=3, label="Rodamiento")

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
    rotaciones.append(arctan(m))

# --- Gráfica de la deflexión ---
X, Y = clean_data(results.x, results.D / mm)
fig.set_figwidth(12)
fig.suptitle(f"Eje vs Flecha del {name} con {round(F/9.8)} kgf en impulsor")
ax2.plot(X, Y, zorder=1)
# Apoyos en deflexión
ax2.scatter([x for x in X_rod], [0 for x in X_rod], c="r", zorder=2)
for i, f in enumerate(reacciones):
    ax2.annotate(f"{round(abs(f/9.8))} kgf\nΔ={abs(round(rad2deg(rotaciones[i]), 4))}°\n", (X_rod[i]+0.03, 0))
ax2.plot([0, Largo], [0, 0], "--", c="GRAY", zorder=0)

# Texto con flechas máximas
x_crit = sum([seg[1] for seg in Eje[0:-2]])
i_crit = min(range(len(Y)), key=lambda i: abs(X[i] - x_crit))
d_crit = Y[i_crit]
fig.text(
    0.50, 0.35,
    f"Flecha máxima: {round(Y[-1], 3)} mm.\nFlecha crítica: {round(d_crit, 3)} mm",
    ha='center'
)

ax1.plot([x_crit, x_crit], [0, Eje[-2][0]], c = "orange")
ax2.scatter(x_crit, d_crit, c = "orange", label = "punto crítico")

# Unidades ejes
ax1.set_ylabel("Diámetro del eje (mm)")
ax2.set_ylabel("Deflexión (mm)")
ax2.set_xlabel("Posición a lo largo del eje (m)")

# Guardado de la figura
minor_ticks = arange(-0.1, 0.6, 0.05)
ax2.set_yticks(minor_ticks, minor=True)

fig.legend()
ax1.xaxis.set_inverted(True)
ax2.xaxis.set_inverted(True)
ax2.grid(visible = True, which = "both", alpha=0.5)
#plt.savefig(f"{name.replace(' ', '_')}.png")
plt.show()
