# Testing

# nombre = preguntar("¿Cómo te llamas? ")
# años = entero(preguntar("¿Cuántos años tienes, " + nombre + "? "))
#
# años = años.parte_real
# nombre = nombre.mayúsculo()
#
# mensaje = nombre + ", vas a tener " + texto(años+1) + " años el año que viene."
# # mensaje = mensaje.mayúsculo()
# escribir(mensaje)
#
# escribir(" ".unir(["Hola", nombre, "!"]))

# Una programa sencilla (es):
#
# nombre = ""
#
# frase_para_escribir = 12 # Número aquí
#
# función letras_de_palabra(palabra):
#     frase_para_escribir = nombre + ", Tienes un"
#     función escribir_letra(letra):
#         escribir(frase_para_escribir.mayúsculo(), letra)
#
#     función con_cada_letra(palabra, func):
#         para letra en palabra:
#             func(letra)
#
#     con_cada_letra(palabra, escribir_letra)
#
# escribir("Doce es", frase_para_escribir.parte_real)
#
# en_bucle = Verdadero
# mientras(en_bucle):
#     nombre = preguntar("¿Cómo te llamas?")
#     si nombre == "Oliver":
#         escribir("Ah, Hola Oliver!")
#     osi nombre == "WebCoder49":
#         escribir("Bienvenido, WebCoder49!")
#     sino:
#         escribir("No te he conocido antes.")
#
#     letras_de_palabra(nombre)
#
#     respuesta = preguntar("¿Quieres jugar otra vez?")
#     en_bucle = (respuesta.mayúsculo() == "SI")
#
# escribir("Adiós!")

# # Tortuga
# importar tortuga
#
# número_lados = entero(preguntar("Cuantos lados tenerá?: "))
# largura_de_lado = entero(preguntar("Largura de cada lado: "))
#
# para i en rango(número_lados):
#     tortuga.avanzar(largura_de_lado)
#     tortuga.girarderecha(360 / número_lados)
#

# Funciónes
# función preguntar_nombre(quien):
#     nombre = preguntar("¿Qué es el nombre de " + quien + "?")
#     devolver nombre
#
# función preguntar_edad_en_meses(quien):
#     edad = entero(preguntar("¿Cuántos años tiene " + quien + "?"))
#     devolver edad * 12
#
#
# nombre = preguntar_nombre("tu amigo/a")
# nombre = nombre.mayúsculo()
# meses = preguntar_edad_en_meses("él/ella")
# meses = meses.parte_real
#
# escribir(nombre + " tiene " + texto(meses) + " meses.")

# Listas

función producir_números(factor):
    número = 0
    mientras (número < 100):
        número = número + factor
        producir número

para número en producir_números:
número = número.parte_real
    escribir("Ha producido el número " + número + "!")

# números = (1, 7, 9, 21, 49)
# =números=
#
# comidas = ["hamburguesas", "raciónes de chorizo", "tomates", "sopas"]
# =comidas=
#
# para número en números:
#     =número=
#     escribir(número.parte_real)
#
# para comida en comidas:
#     =comida=
#     comida = comida.mayúsculo()
#     para número en números:
#         escribir("Quiero " + texto(número) + " " + comida + ".")