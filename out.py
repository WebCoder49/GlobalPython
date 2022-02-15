nombre = ""
frase_de_escribir = 12
def letras_de_palabra ( palabra ) : # Scope[('local', {'nombre': ('nombre', {}, None, [['str']]), 'frase_de_escribir': ('frase_de_escribir', {}, None, [['int'], ['float']])}, None, []), ('Pushed', {}, None, [])]
    frase_de_escribir = nombre + ", Tienes un"
    def escribir_letra ( letra ) : # Scope[('local', {'nombre': ('nombre', {}, None, [['str']]), 'frase_de_escribir': ('frase_de_escribir', {}, None, [['int'], ['float']])}, None, []), ('Pushed', {'frase_de_escribir': ('frase_de_escribir', {}, None, [['nombre']])}, None, []), ('Pushed', {}, None, [])]
        print(frase_de_escribir.upper(),letra)
    
    def con_cada_letra ( palabra,func ) : # Scope[('local', {'nombre': ('nombre', {}, None, [['str']]), 'frase_de_escribir': ('frase_de_escribir', {}, None, [['int'], ['float']])}, None, []), ('Pushed', {'frase_de_escribir': ('frase_de_escribir', {}, None, [['nombre']])}, None, []), ('Pushed', {}, None, [])]
        for letra in palabra :
            func(letra)
        
    
    con_cada_letra(palabra,escribir_letra)

print("Doce es",frase_de_escribir.real)
en_bucle = True
while (en_bucle) :
    nombre = input("¿Cómo te llamas?")
    if nombre == "Oliver" :
        print("Ah, Hola Oliver!")
    
    elif nombre == "WebCoder49" :
        print("Bienvenido, WebCoder49!")
    
    else :
        print("No te he conocido antes.")
    
    letras_de_palabra(nombre)
    respuesta = input("¿Quieres jugar otra vez?")
    en_bucle = (respuesta.upper() == "SI")

print("Adiós!")