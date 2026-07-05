from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os

# Configurazione modelli
modelli = {
    "1": "model_it",
    "2": "model_en",
    "3": "model_de",
    "4": "model_es",
    "5": "model_fr",
    "6": "model_ru",
    "7": "model_cn",
    "8": "model_ko",
    "9": "model_ja"
}

print("Seleziona la lingua per il modello:")
for k, v in modelli.items():
    print(f"{k}: {v}")

scelta = input("Inserisci il numero: ")
nome_cartella = modelli.get(scelta, "model_en") # Default inglese

# Carica il modello selezionato
print(f"Caricamento {nome_cartella} in corso...")
model = Model(nome_cartella)
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()

# Trova tutti gli ID che contengono "CABLE" nel nome
cables = []
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if "CABLE" in dev['name'].upper():
        cables.append(i)
        print(f"Trovato dispositivo CABLE all'ID {i}: {dev['name']}")

if not cables:
    print("Errore: Nessun dispositivo VB-Cable trovato!")
    exit()

# Prova ad aprire il primo della lista (ID 1 come da tuo log)
target_id = cables[0]
print(f"Tentativo di ascolto sul dispositivo ID {target_id}...")

stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, 
                input_device_index=target_id, frames_per_buffer=4000)
stream.start_stream()

print("--- VOSK in ascolto ---")
print("Le trascrizioni verranno salvate anche in 'trascrizione.txt'")

while True:
    try:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            risultato = json.loads(rec.Result())
            testo = risultato.get('text', '')
            if testo:
                print(">>> TRASCRITTO: " + testo)
                # Scrittura su file TXT
                with open("trascrizione.txt", "a", encoding="utf-8") as f:
                    f.write(testo + "\n")
    except Exception as e:
        print(f"Errore flusso audio: {e}")
        break