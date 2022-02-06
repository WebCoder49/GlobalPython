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

en_bucle = Verdadero
mientras(en_bucle):
    nombre = preguntar("¿Cómo te llamas?")

    si nombre == "Oliver":
        escribir("Ah, Hola Oliver!")
    osi nombre == "WebCoder49":
        escribir("Bienvenido, WebCoder49!")
    sino:
        escribir("No te he conocido antes.")

    # para letra en nombre:
    #   escribir("Tienes un"+letra)

    respuesta = preguntar("¿Quieres jugar otra vez?")
    en_bucle = respuesta.mayúsculo() == "SI"

escribir(nombre, en_bucle)