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

nombre = ""

frase_de_escribir = 12 # Número en este "scope"

función letras_de_palabra(palabra):
    frase_de_escribir = nombre + ", Tienes un"
    función escribir_letra(letra):
        escribir(frase_de_escribir.mayúsculo(), letra)

    función con_cada_letra(palabra, func):
        para letra en palabra:
            func(letra)

    con_cada_letra(palabra, escribir_letra)

escribir("Doce es", frase_de_escribir.parte_real)

en_bucle = Verdadero
mientras(en_bucle):
    nombre = preguntar("¿Cómo te llamas?")
    si nombre == "Oliver":
        escribir("Ah, Hola Oliver!")
    osi nombre == "WebCoder49":
        escribir("Bienvenido, WebCoder49!")
    sino:
        escribir("No te he conocido antes.")

    letras_de_palabra(nombre)

    respuesta = preguntar("¿Quieres jugar otra vez?")
    en_bucle = (respuesta.mayúsculo() == "SI")

escribir("Adiós!")
