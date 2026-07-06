import sys
sys.path.append('/var/src/src/SAS-PROD/Sistema-SAS-PROD/backend')
from database import query_db
print(query_db("SELECT id, nome_completo, status, tipo_atendimento FROM agendamentos ORDER BY id DESC LIMIT 5"))
