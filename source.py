# Importar
importar tortuga

lados = entero(preguntar("¿Cuántos lados quieres?"))

# Dibujar
t = tortuga.Tortuga()
tiempo = tortuga.tiempo
para i en rango(lados):
    t.avanzar(1000/lados)
    t.girar_derecha(360 / lados)
    tiempo.esperar(3 / lados)

escribir(" ".unir("Tiene", lados, "lados"))

t.parar()