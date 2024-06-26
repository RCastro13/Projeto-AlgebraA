import time
import os
import threading
from sympy import primefactors, factorint
from functools import reduce
from sympy.ntheory.residue_ntheory import discrete_log

def handle_timeout():
    print("Tempo limite atingido; Execucao terminada.")
    os._exit(1)


def terminator(func):
    def wrapper(*args, **kwargs):
        TIMEOUT = 300  # tempo limite em segundos
        alarm = threading.Timer(TIMEOUT, handle_timeout)
        alarm.start()
        
        result = None
        try:
            result = func(*args, **kwargs)
        finally:
            alarm.cancel()
        
        return result

    return wrapper


def mdc(a, b):
    """
    :param a: número
    :param b: número
    :return: retorna o mdc entre 'a' e 'b'
    """
    while b:
        a, b = b, a % b
    return a

def mod_exp(base, exp, mod):
    """
    :param base: base do expoente
    :param exp: expoente
    :param mod: módulo 
    :return: retorna 'base' elevado à 'exp' mod 'mod'
    """

    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2

    return result

def all_primes(n):
    """
    :param n: número a ser fatorado
    :return: retorna 'n' fatorado com repetição de fatores
    """
    fatores = factorint(n)
    resultado = []
    for fator, potencia in fatores.items():
        resultado.extend([fator] * potencia)
    return resultado

def fatoraDistinctPrimes(n):
    """
    :param n: número a ser fatorado
    :return: retorna 'n' fatorado sem repetição de número (Ex.: 2,2 -> 2)
    """
    return primefactors(n)

def fatoraPrimeExp(n):
    """
    :param n: número a ser fatorado
    :return: retorna 'n' fatorado com repetição de fatores
    """
    return all_primes(n)

def millerRabin(n):
    """
    :param n: número recebido na entrada
    :return: retorna true or false caso 'n' seja ou não primo
    """ 
    #Lista de 60 primos para teste da função
    primeList = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281]
    
    #cálculo de k e m tal que n-1 = 2^k * m
    k, m = 0, n - 1
    while m % 2 == 0:
        m //= 2
        k += 1
    
    #quantidade de a's a ser testado (numIter)
    for a in primeList:
        if mdc(a,n) != 1:
            return False
        
        x = mod_exp(a, m, n)

        #se x mod n = 1 ou -1 então 'n' é possível primo
        if x == 1 or x == n - 1:
            continue
        
        for i in range(1, k):
            x = mod_exp(x, 2, n)
            #se x mod n = -1 então 'n' é possível primo
            if x == n - 1:
                break
        else:
            return False #SE EU USAR UM ELIF X==1 AO INVES DESSE ELSE DO FOR NÃO FUNCIONA
            
    return True

def nextPrime(n):
    """
    :param n: número recebido na entrada
    :return: retorna o próximo primo após 'n'
    """
    start_time = time.time()

    if n % 2 == 0:
        newPrime = n+1
        
    else:
        newPrime = n+2

    while(True):
        result = millerRabin(newPrime)
        if result == False:
            newPrime = newPrime + 2
        else:
            break

    end_time = time.time()
    execution_time = end_time - start_time
    print("Tempo Gasto para achar o menor primo maior que N: ", execution_time)

    return newPrime

def find_generator(p):
    """
    :param p: número primo
    :return: retorna um gerador do grupo multiplicativo Zp
    """
    start_time = time.time()

    #fatoração do modulo -1
    phi = p - 1
    factors = fatoraDistinctPrimes(phi)
    #print("FATORES DE ", phi, ": ", factors)

    for g in range(2, p):
        is_generator = True
        for factor in factors:
            power = phi//factor
            if mod_exp(g, power, p) == 1:
                is_generator = False
                break
        if is_generator:
            #print("GERADOR: ", g)
            end_time = time.time()
            execution_time = end_time - start_time
            print("Tempo Gasto para achar o gerador: ", execution_time)
            return g
    
    return None

def chinese_remainder_theorem(residues, moduli):
    """
    :param residues: números congruentes no TCR
    :param moduli: módulos do TCR
    :return: retorna o valor de N -> aplicação do TCR
    """

    product = reduce(lambda x, y: x * y, moduli)
    result = 0
    for residue, modulus in zip(residues, moduli):
        p = product // modulus
        #_, inv, _ = egcd(p, modulus)
        inv = mdc(p, modulus)
        result += residue * inv * p
        
    return result % product


@terminator
def pohlig_hellman(base, a, modulo):
    """
    :param base: base do logaritmo discreto
    :param a: será calculado logaritmo de 'a'
    :param modulo: módulo do logaritmo
    :return: retorna o logaritmo discreto de 'a' na base 'base' modulo 'modulo'
    """

    #fatoração do modulo -1 
    phi = modulo - 1
    factors = fatoraPrimeExp(phi)
    #print("FATORES DE ", phi, ": ", factors)

    #fatores mapeados com relação a sua potência
    powers = []
    primesWithPower = list(set(map(lambda n: n**factors.count(n), factors)))

    #cálculo das potências a serem utilizadas
    for prime in primesWithPower:
        powers.append(int((modulo-1) / prime))
    
    #cálculo dos intervalos máximos de cada variável
    intervals = []
    for power in powers:
        intervals.append(int((modulo-1) / power))

    #Encontrando os valores n1,n2...nk
    chineseNumbers = []
    tam = len(intervals)
    for j in range (0, tam, 1):
        leftMod = mod_exp(a, powers[j], modulo)
        rightMod = mod_exp(base, powers[j], modulo)
       
        # for i in range(1, intervals[j]):
        #     resp = mod_exp(rightMod, i, modulo)
        #     if resp == leftMod:
        #         chineseNumbers.append(i)
        #         print("FIZ APPEND DE ", i)
        #         break

        dlog = discrete_log(modulo, leftMod, rightMod)
        chineseNumbers.append(dlog)

    resp = chinese_remainder_theorem(chineseNumbers, intervals)

    return resp

def ler_numeros_do_arquivo(nome_arquivo):
    """
    :param nome_arquivo: nome do arquivo de entrada
    :return: retorna os 2 números de input
    """
    try:
        with open(nome_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
            if len(linhas) < 2:
                raise ValueError("O arquivo deve conter pelo menos duas linhas.")

            numero_primeira_linha = int(linhas[0].strip())
            numero_segunda_linha = int(linhas[1].strip())

            return numero_primeira_linha, numero_segunda_linha

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
    except ValueError as ve:
        print(f"Erro: {ve}")

nome_arquivo = 'entrada.txt'
n, a = ler_numeros_do_arquivo(nome_arquivo)

#Encontrando o menor primo maior que N
newPrime = nextPrime(n)
print("O menor primo maior que", n, "é", newPrime)

#Encontrando um gerador de Zn
generator = find_generator(newPrime)
print("Um gerador de Zn é", generator)

#Retornar o logaritmo discreto de 'a' módulo 'p' na base 'g'
start_time = time.time()
logDiscreto = pohlig_hellman(generator, a, newPrime)
end_time = time.time()
execution_time = end_time - start_time
print("Tempo Gasto para calcular o logaritmo discreto: ", execution_time)

print("O logaritmo de", a, "na base", generator, "modulo", newPrime, "é", logDiscreto)