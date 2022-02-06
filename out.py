en_bucle = True
nombre = input("¿Cómo te llamas?")
if nombre == "Oliver" :
  print("Ah, Hola Oliver!")
elif nombre == "WebCoder49" :
  print("Bienvenido, WebCoder49!")
else :
  print("No te he conocido antes.")
respuesta = input("¿Quieres jugar otra vez?")
en_bucle = respuesta.upper() == "SI"
print(nombre,en_bucle)