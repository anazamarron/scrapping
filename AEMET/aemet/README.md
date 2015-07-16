# Datos del tiempo de la web de la AEMET

Obtención de los datos del tiempo en España de la web de la aemet y guarda la información en MongoDB. 

se obtienen 2 dataset distintos:

    1.- Previsión del tiempo por población para los próximos 6 días
        - Localidad
        - Poblacion
        - Provincia
        - Longitud
        - Latitud
        - Fecha
            - Probabilidad de precipitaciones
            - Cota de nieve
            - Estado del cielo
            - Viento
                - dirección
                - velocidad
                - racha max
            - Temperatura
                - max
                - min
            - Sensación Térmica
                - max
                - min
            - Humedad Relativa
                - max 
                - min
            - Radicación UV
        
    2.- Previsión del tiempo en las playas (2 días)
        - Localidad
        - Poblacion
        - Provincia
        - nombre de la playa
        - Longitud
        - Latitud
        - Fecha
            - Temperatura_máxima
            - Sensación térmica
            - Índice uv
            - Temperatura_agua
            - Cielo mañana
            - Cielo tarde
            - Viento mañana
            - Viento tarde
            - Oleaje mañana
            - Oleaje tarde
            - Hora Pleamar
            - Hora Bajamar
    

### Todo's
- La idea es añadir además una api de consulta a mongo para poder obtener la información


