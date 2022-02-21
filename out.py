def producir_números ( factor ) :
    número = 0
    while (número < 100) :
        número = número + factor
        yield número
    

for número in producir_números :
    número = número.real
    print("Ha producido el número " + número + "!")
