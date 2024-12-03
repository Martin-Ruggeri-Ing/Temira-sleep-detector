import rsa

def generar_claves():
    clave_publica, clave_privada = rsa.newkeys(2048)
    return clave_publica, clave_privada

def guardar_claves(clave_publica, clave_privada):
    with open('clave_publica.pem', 'wb') as archivo:
        archivo.write(clave_publica.save_pkcs1())
    with open('clave_privada.pem', 'wb') as archivo:
        archivo.write(clave_privada.save_pkcs1())

def leer_clave(tipo):
    clave = None
    with open(f'clave_{tipo}.pem', 'r') as archivo:
        clave = rsa.PrivateKey.load_pkcs1(archivo.read().encode()) if tipo == 'privada' else rsa.PublicKey.load_pkcs1(archivo.read().encode())
    return clave

if __name__ == '__main__':
    clave_publica, clave_privada = generar_claves()
    guardar_claves(clave_publica, clave_privada)
