import pyfirmata2
import time
import json
from LCD import LCD

# Debug-modus inschakelen (True om debugging aan te zetten, False om uit te zetten)
DEBUG = True


def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")


# Laad de configuratie
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        debug_print("Configuratie geladen.")
except FileNotFoundError:
    print("config.json bestand niet gevonden!")
    exit()

board = pyfirmata2.Arduino('COM3')
board.samplingOn(300)
lcd = LCD(board)

# Definieer de pinnen voor de sensoren
detection_pin_add = board.get_pin('d:2:u')
detection_pin_min = board.get_pin('d:3:u')

inkomende_bezoekers = config["inkomende_bezoekers"]
verwerkings_snelheid = config["verwerkings_snelheid"]
min_personen_wachtrij = config["min_personen_wachtrij"]
gem_personen_wachtrij = config["gem_personen_wachtrij"]
max_personen_wachtrij = config["max_personen_wachtrij"]


def startup():
    debug_print("Startup-functie gestart.")
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.print("Systeem Start...")
    time.sleep(3)
    lcd.clear()
    lcd.set_cursor(0, 1)
    lcd.print("Opgestart.")
    time.sleep(3)
    lcd.clear()
    debug_print("Startup-functie voltooid.")

## -- Trotse Code -- ##


def add_callback(released):
    global inkomende_bezoekers
    if not released:
        if inkomende_bezoekers < max_personen_wachtrij:
            inkomende_bezoekers += 1
            debug_print(f"Inkomende bezoekers verhoogd naar {
                        inkomende_bezoekers}.")
            check_count()
            display()
        else:
            print("Maximum aantal bereikt, kan niemand meer naar binnen.")


def min_callback(released):
    global inkomende_bezoekers
    if not released:
        if inkomende_bezoekers > min_personen_wachtrij:
            inkomende_bezoekers -= 1
            debug_print(f"Inkomende bezoekers verlaagd naar {
                        inkomende_bezoekers}.")
            check_count()
            display()
        else:
            print("Er zijn geen mensen om eruit te laten.")

## -- Trotse Code -- ##


def check_count():
    global inkomende_bezoekers
    debug_print(f"Bezoekers checken: {inkomende_bezoekers}.")
    if inkomende_bezoekers == max_personen_wachtrij:
        board.digital[13].write(1)  # Rood
        board.digital[12].write(0)
        board.digital[11].write(0)
    elif inkomende_bezoekers > gem_personen_wachtrij:
        board.digital[13].write(0)
        board.digital[12].write(1)  # Geel
        board.digital[11].write(0)
    elif inkomende_bezoekers == min_personen_wachtrij or inkomende_bezoekers < gem_personen_wachtrij:
        board.digital[13].write(0)
        board.digital[12].write(0)
        board.digital[11].write(1)  # Groen


def display():
    global inkomende_bezoekers, verwerkings_snelheid
    wachttijd = round(inkomende_bezoekers / verwerkings_snelheid, 2)
    debug_print(f"Wachttijd berekend: {wachttijd} minuten.")

    lcd.clear()
    lcd.print(f"{inkomende_bezoekers} van de 30")
    lcd.set_cursor(0, 1)
    lcd.print(f"Wachttijd: {wachttijd} min")

    debug_print(f"LCD display bijgewerkt met bezoekers: {
                inkomende_bezoekers} en wachttijd: {wachttijd}.")


# Registreer de callbacks
detection_pin_add.register_callback(add_callback)
detection_pin_min.register_callback(min_callback)

try:
    print("*Systeem start op...")
    startup()
    print("*Begin checken van bezoekersaantal.*")
    check_count()
    display()
    while True:
        time.sleep(3)
        display()
except KeyboardInterrupt:
    print('Programma gestopt door gebruiker.')
    lcd.clear()
finally:
    debug_print("Programma wordt afgesloten.")
    board.exit()
    print("Verbinding gestopt")
