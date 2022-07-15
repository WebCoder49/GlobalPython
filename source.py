# # Función
# función hacer_error():
#     """Error!"""
#     escribir(1 / 0)
#
# # Empezar aquí
# hacer_error()

# # Listos
# números = [2, 3, 5, 7, 3.14]
# para número en números:
#     escribir("1 /", número, "=", 1 / número)

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

# # Una programa sencilla (es):
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
# en_bucle = Verdad
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