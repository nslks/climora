# Persistenz-Layer entfernt

Die früheren Module `repositories/measurement_repository_interface.py` und
`repositories/db_service_measurement_repository.py` wurden bewusst entfernt,
um den Data Collector strikt von Persistenzdetails zu entkoppeln. Stattdessen
nutzt der Service jetzt direkt den bereits existierenden
`shared.clients.db_service_client.DbServiceClient`, um Messwerte an den neuen
DB Service zu senden.

Ältere Commits enthalten die ursprünglichen Dateien, falls sie für Referenzen
benötigt werden.
