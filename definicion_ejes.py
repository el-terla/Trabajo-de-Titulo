
class EjeConfig:
    def __init__(self, nombre, fuerza, apoyos, segmentos):
        self.nombre = nombre
        self.F = fuerza
        self.apoyos = apoyos
        self.Eje = segmentos
        self.seg_crit = 0 ###########

def eje_opt(var, D1, D2, F):
    eje = EjeConfig(
        nombre="Eje Nuevo optimizado",
        fuerza=F,
        apoyos=[0, 4],
        segmentos=[
            [55, 21],
            [70, 119],
            [70, 17.32, 90],
            [90, var],
            [90, 15],
            [102, 6],
            [102, 4.33, D1],
            [D1, 144.51],
            [D1, 60.16, D2],
            [D2, 161.1],
            [D2, 28.5, 53],
            [45, 30]
        ]
    )
    return eje

eje_viejo = EjeConfig(
    nombre="Eje Actual",
    fuerza=5253,
    apoyos=[0, 7],
    segmentos=[
        [55, 21],
        [70, 119],
        [70, 32.04, 107],
        [107, 153.13],
        [107, 4.33, 102],
        [102, 6],
        [90, 15],
        [90, 169.84],
        [90, 60.16, 60],
        [60, 161.5],
        [60, 28.5, 53],
        [45, 30]
    ]
)
eje_modificado = EjeConfig(
    nombre="Eje Diametros Modificados",
    fuerza=6310,
    apoyos=[0, 4],
    segmentos=[
        [55, 21],
        [70, 119],
        [70, 17.32, 90],
        [90, 193.18],
        [90, 15],
        [102, 6],
        [102, 4.33, 107],
        [107, 144.51],
        [107, 60.16, 70],
        [70, 161.5],
        [70, 28.51, 53],
        [45, 30]
    ]
)
#eje_optimizado = eje_opt(69, 107, 70, 6855)
eje_optimizado_def = eje_opt(116, 106, 70, 6680)

eje_827 = EjeConfig(
    nombre = "HDE827B",
    fuerza = 900*9.8,
    apoyos = [0, 3],
    segmentos=[
        [60 ,31],
        [77, 150.5],
        [60, 15.5],
        [60, 52.37],
        [58, 153.17],
        [48, 40],
        [48, 7]
    ]
)
