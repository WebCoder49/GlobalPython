nombre = input("¿Cómo te llamas? ")
años = int(input("¿Cuántos años tienes, " + nombre + "? "))
años = años.real
nombre = nombre.upper()
mensaje = nombre + ", vas a tener " + str(años + 1) + " años el año que viene."
print(mensaje)
print(" ".join(["Hola", nombre, "!"]))
nombre = ""
frase_para_escribir = 12


def letras_de_palabra(palabra):
    frase_para_escribir = nombre + ", Tienes un"

    def escribir_letra(letra):
        print(frase_para_escribir.upper(), letra)

    def con_cada_letra(palabra, func):
        for letra in palabra:
            func(letra)

    con_cada_letra(palabra, escribir_letra)


print("Doce es", frase_para_escribir.real)
en_bucle = True
while (en_bucle):
    nombre = input("¿Cómo te llamas?")
    if nombre == "Oliver":
        print("Ah, Hola Oliver!")
    elif nombre == "WebCoder49":
        print("Bienvenido, WebCoder49!")
    else:
        print("No te he conocido antes.")
    letras_de_palabra(nombre)
    respuesta = input("¿Quieres jugar otra vez?")
    en_bucle = (respuesta.upper() == "SI")
print("Adiós!")
import tortuga as t

número_lados = int(input("Cuantos lados tenerá?: "))
largura_de_lado = int(input("Largura de cada lado: "))
for i in range(número_lados):
    t.avanzar(largura_de_lado)
    t.girarderecha(360 / número_lados)


def preguntar_nombre(quien):
    nombre = input("¿Qué es el nombre de " + quien + "?")
    return nombre


def preguntar_edad_en_meses(quien):
    edad = int(input("¿Cuántos años tiene " + quien + "?"))
    return edad * 12


nombre = preguntar_nombre("tu amigo/a")
nombre = nombre.upper()
meses = preguntar_edad_en_meses("él/ella")
meses = meses.real
print(nombre + " tiene " + str(meses) + " meses.")


def producir_números(factor):
    número = 0
    while (número < (100 - factor)):
        número = número + factor
        yield número


for número in producir_números(3):
    número = número.real
    print("Ha producido el número " + str(número) + "!")
números = (1, 7, 9, 21, 49)

comidas = ["hamburguesas", "raciónes de chorizo", "tomates", "sopas"]

for número in números:
    print(número.real)
for comida in comidas:

    comida = comida.mayúsculo()
    for número in números:
        print("Quiero " + str(número) + " " + comida + ".")
a = 1 + 2 * 3 == (7).real() and (1 == 0.4 + 0.3 * 0.2).real() == 1
b = "Hola, " + "a".upper() * 3 + " es una palabra."
print(a, b)
