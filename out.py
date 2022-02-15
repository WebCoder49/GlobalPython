import  as 
número_lados = int(input("Cuantos lados tenerá?: "))
largura_de_lado = int(input("Largura de cada lado: "))
for i in range(número_lados) :
    tortuga.fd(largura_de_lado)
    tortuga.rt(360 / número_lados)
