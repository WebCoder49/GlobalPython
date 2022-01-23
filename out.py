nombre = preguntar("¿Cómo te llamas? ")
años = entero(preguntar("¿Cuántos años tienes, " + nombre + "? "))
mensaje = nombre + ", vas a tener " + texto(años + 1) + " años el año que viene."
escribir(mensaje)
escribir(" ".unir(["Hola",nombre,"!"]))