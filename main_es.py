import random
import sys

# Inicialización del mazo (sin jokers, sin figuras rojas)
SUITS = ['♠', '♣', '♦', '♥']
VALUES = list(range(2, 11)) + ['A', 'J', 'Q', 'K']
DECK = [f"{v}{s}" for s in SUITS for v in VALUES if not (s in ['♦', '♥'] and isinstance(v, str))]

# Estado del juego
state = {
    "vida": 20,
    "arma": 0,
    "descartadas": 0,
    "ultima_combatida": 0,
    "habitacion": [],
    "mazo": DECK.copy(),
    "pocion_usada": False,
    "renovacion_usada": False
}

# Funciones auxiliares
def parse_valor(carta):
    valores = {
        'A': 14,
        'K': 13,
        'Q': 12,
        'J': 11
    }
    valor = carta[:-1]  # Removes the suit symbol
    return int(valores.get(valor, valor))  # Returns mapped value or converts to int

def palo(carta):
    return carta[-1]

def mezclar():
    random.shuffle(state["mazo"])

def robar_inicial():
    state["pocion_usada"] = False
    state["habitacion"] = []
    for _ in range(4):
        if state["mazo"]:
            state["habitacion"].append(state["mazo"].pop(0))

def mostrar_estado():
    print(f"\nVida: {state['vida']} | Arma: {state['arma']} | Ultima combatida: {state['ultima_combatida']} | Descartadas: {state['descartadas']}")
    print("Habitacion:", ", ".join(state["habitacion"]))
    print("Cartas restantes en mazo:", len(state["mazo"]))

def perder_vida(valor, tipo):
    state["vida"] -= valor
    tipo_ataques = {
        1: "Pelea sin armas.",
        2: "Has usado tu arma.",
    }
    texto = tipo_ataques.get(tipo, "Pelea sin armas.") 
    print(f"{texto} Recibes {valor} de daño.")

def activar_carta(indice):
    try:
        carta = state["habitacion"].pop(indice-1)
    except IndexError:
        print("Índice inválido.")
        return

    valor = parse_valor(carta)
    palo_carta = palo(carta)

    if palo_carta == '♥':
        if state["pocion_usada"] == False:
            state["pocion_usada"] = True
            ganancia = min(20 - state["vida"], valor)
            state["vida"] += ganancia
            print(f"Recuperas {ganancia} de vida.")
        else:
            print(f"Ya te usaste una pocion esta ronda.")
    elif palo_carta == '♦':
        state["arma"] = valor
        state["ultima_combatida"] = 0
        print(f"Equipas un arma de valor {valor}.")
    else:
        if state["arma"] == 0 or (valor >= state["ultima_combatida"] and state["ultima_combatida"] != 0):
            perder_vida(valor,1)
        else: 
            print("¿Usas tu arma? (Y or N)")
            opcion = input(">> ").strip().lower()
            if  opcion == 'n':
                perder_vida(valor,1)
            else:
                dano = max(valor - state["arma"], 0)
                state["ultima_combatida"] = valor
                perder_vida(dano,2)
    state["descartadas"] += 1

    if len(state["habitacion"]) == 1:
        state["pocion_usada"] = False
        state["renovacion_usada"] = False
        print("Robas 3 cartas más (trigger de habitacion con 1 carta)...")
        for _ in range(3):
            if state["mazo"]:
                state["habitacion"].append(state["mazo"].pop(0))

    verificar_derrota()
    verificar_victoria()

def descartar_y_renovar_habitacion():
    state["renovacion_usada"] = True
    state["mazo"].extend(state["habitacion"])
    state["habitacion"] = []
    robar_inicial()
    print("habitacion renovada.")

def verificar_derrota():
    if state["vida"] <= 0:
        print("\n Has sido derrotado. Juego reiniciado.")
        reiniciar()

def verificar_victoria():
    if not state["mazo"] and not state["habitacion"]:
        print("\n Has ganado. Juego reiniciado.")
        reiniciar()

def reiniciar():
    state["vida"] = 20
    state["arma"] = 0
    state["descartadas"] = 0
    state["ultima_combatida"] = 0
    state["mazo"] = DECK.copy()
    mezclar()
    robar_inicial()
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        for _ in range(30):
            state["mazo"].pop(0)

# Menú principal
def main():
    reiniciar()
    while True:
        mostrar_estado()
        print("\nOpciones:")
        print(" [1-4] Activar carta en esa posición")
        if len(state["habitacion"]) == 4 and state["renovacion_usada"]==False:
            print(" r - Renovar habitacion")
        print(" q - Salir")
        opcion = input(">> ").strip().lower()

        if opcion in ['4', '1', '2', '3']:
            activar_carta(int(opcion))
        elif opcion == 'r' and len(state["habitacion"]) == 4 and state["renovacion_usada"]==False and state["mazo"]:
            descartar_y_renovar_habitacion()
        elif opcion == 'q':
            print("¡Hasta luego!")
            break
        else:
            print("Comando no válido.")

if __name__ == "__main__":
    main()
