
class Kullanici:
    def __init__(self,isim,yas):
        self.isim = isim
        self.yas = yas
        print(isim,'is a customer and he is',yas,'years old.')
    
    def selamla(self):
        print("ooo, hosgeldin! benim adim {isim}".format(isim = self.isim))

class Musteri(Kullanici):
    def __init__(self):
        super().__init__('hhsomek','30')
    
        
hhsomek = Musteri()
hhsomek.selamla()



































