import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.db import query_db

try:
    print("Appointments for 2026-01-14:")
    appts_14 = query_db("SELECT * FROM agendamentos WHERE data_agendamento = '2026-01-14'")
    for a in appts_14:
        print(f"  - {a['hora_inicio']} | {a['nome_completo']} | Atendente ID: {a['atendente_id']}")

    print("\nAppointments for 2026-01-15:")
    appts_15 = query_db("SELECT * FROM agendamentos WHERE data_agendamento = '2026-01-15'")
    for a in appts_15:
        print(f"  - {a['hora_inicio']} | {a['nome_completo']} | Atendente ID: {a['atendente_id']}")

    print("\nAppointments for 2026-01-16:")
    appts_16 = query_db("SELECT * FROM agendamentos WHERE data_agendamento = '2026-01-16'")
    for a in appts_16:
        print(f"  - {a['hora_inicio']} | {a['nome_completo']} | Atendente ID: {a['atendente_id']}")

except Exception as e:
    print(f"Error: {e}")
