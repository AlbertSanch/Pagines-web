"""Genera las páginas «¿Cuánto gasta…?» de cada electrodoméstico con el precio actual de la luz.

Lee el precio medio de la luz de ahorrometro/datos/luz.json (lo genera actualizar_luz.py) y crea:
  - ahorrometro/cuanto-gasta/<aparato>.html: una página por aparato con su calculadora,
    una tabla de consumo según el modelo, trucos y preguntas frecuentes;
  - ahorrometro/consumo-electrodomesticos.html: la tabla de todos los aparatos;
  - las entradas del sitemap.xml entre <!-- CONSUMO:INICIO --> y <!-- CONSUMO:FIN -->;
  - el ejemplo y las tablas de calculadoras/consumo-electrico.html entre <!-- CONSUMO-CALC:INICIO --> y <!-- CONSUMO-CALC:FIN -->.
Los costes van escritos en el HTML para que Google los lea, y se recalculan cada vez que
cambia el precio de la luz. La cabecera y el pie se copian de calculadoras/coste-viaje-coche.html.

Uso: python scripts/paginas_consumo.py
"""

import json
import re
from datetime import date
from html import escape
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "ahorrometro"
DOMINIO = "https://ahorrometro.es"
CARPETA = "cuanto-gasta"
PRECIO_POR_DEFECTO = 0.16  # €/kWh con impuestos, si no hay datos de Red Eléctrica

# modo «potencia»: vatios × horas al día × días al mes × factor (parte del tiempo a plena potencia)
# modo «ciclo»: kWh por uso × usos a la semana
APARATOS = [
    dict(slug="placa-de-induccion", nombre="Placa de inducción", art="una placa de inducción", icono="🍳",
         modo="potencia", w=2000, horas=1, dias=30, factor=0.6,
         uso="1 hora al día, con un fuego a potencia media",
         modelos=[("Un fuego a potencia media", 1200), ("Un fuego a potencia máxima", 2300), ("Dos fuegos a la vez", 3500)],
         texto="La inducción calienta directamente el recipiente, así que aprovecha alrededor del 85–90 % de la energía, frente al 70 % de una vitrocerámica. Su potencia máxima es alta, pero casi nunca se usa entera: lo normal es cocinar a potencia media y que el fuego module.",
         trucos=["Usa recipientes del tamaño del fuego y con fondo plano.", "Tapa las ollas: hierven antes y gastan menos.", "Usa la función «booster» solo para hervir agua, no para cocinar."],
         faq=[("¿Gasta más la inducción o la vitrocerámica?", "La inducción gasta entre un 20 y un 30 % menos para cocinar lo mismo, porque calienta el recipiente directamente y desperdicia menos calor."),
              ("¿Necesito más potencia contratada para una placa de inducción?", "Si usas varios fuegos a la vez junto con el horno o la lavadora, puedes superar los 4–5 kW. Las placas permiten limitar su potencia máxima para que no salte el ICP.")]),
    dict(slug="vitroceramica", nombre="Vitrocerámica", art="una vitrocerámica", icono="🔥",
         modo="potencia", w=1800, horas=1, dias=30, factor=0.65,
         uso="1 hora al día, con un fuego a potencia media",
         modelos=[("Fuego pequeño", 1200), ("Fuego grande", 2000), ("Dos fuegos a la vez", 3200)],
         texto="La vitrocerámica calienta una resistencia bajo el cristal, que después transmite el calor al recipiente. Es más lenta y menos eficiente que la inducción, y el cristal sigue caliente un rato después de apagarla, algo que puedes aprovechar.",
         trucos=["Apaga el fuego 3–5 minutos antes de terminar: el calor residual acaba de cocinar.", "Mantén el cristal limpio: la suciedad empeora la transmisión de calor.", "Usa la olla exprés para guisos y legumbres."],
         faq=[("¿Cuánto consume una vitrocerámica por hora?", "Entre 0,8 y 1,3 kWh por hora con un fuego a potencia media, porque la resistencia se enciende y se apaga para mantener la temperatura."),
              ("¿Compensa cambiar la vitrocerámica por una inducción?", "Solo si cocinas mucho. El ahorro suele ser de 20 a 40 euros al año, así que la placa tarda años en amortizarse si cambias solo por el consumo.")]),
    dict(slug="horno-electrico", nombre="Horno eléctrico", art="un horno eléctrico", icono="🥧",
         modo="potencia", w=2000, horas=1, dias=8, factor=0.55,
         uso="1 hora, unas 2 veces a la semana",
         modelos=[("Horno pequeño de sobremesa", 1200), ("Horno empotrado normal", 2200), ("Horno grande o con pirólisis", 3500)],
         texto="El horno gasta mucho al principio, mientras se calienta, y después solo enciende las resistencias de vez en cuando para mantener la temperatura. Por eso una hora de horno a 200 °C consume alrededor de 1–1,2 kWh, no los 2 kWh de su potencia máxima.",
         trucos=["No abras la puerta mientras cocinas: cada vez pierdes unos 20 °C.", "Aprovecha para cocinar varias cosas a la vez.", "Para raciones pequeñas, la freidora de aire o el microondas gastan mucho menos."],
         faq=[("¿Cuánto cuesta tener el horno encendido una hora?", "Con el precio medio de la luz, entre 20 y 35 céntimos, según el modelo y la temperatura."),
              ("¿Gasta más el horno o la freidora de aire?", "La freidora de aire gasta alrededor de la mitad para la misma comida, porque calienta un espacio mucho más pequeño y tarda menos.")]),
    dict(slug="lavadora", nombre="Lavadora", art="una lavadora", icono="🧺",
         modo="ciclo", kwh=0.9, usos=4,
         uso="4 lavados a la semana a 40 °C",
         modelos=[("Lavado en frío (20 °C)", 0.3), ("Lavado a 40 °C", 0.9), ("Lavado a 60 °C", 1.5), ("Lavado a 90 °C", 2.3)],
         texto="Casi toda la electricidad de una lavadora se usa para calentar el agua. Por eso la temperatura del programa es lo que más cambia el gasto: lavar a 30 °C en vez de a 60 °C reduce el consumo a menos de la mitad.",
         trucos=["Lava en frío o a 30 °C: los detergentes actuales limpian bien a baja temperatura.", "Llena el tambor: dos medias cargas gastan casi el doble.", "Usa el programa eco aunque tarde más: gasta menos energía."],
         faq=[("¿Cuánto cuesta poner una lavadora?", "Un lavado a 40 °C cuesta entre 15 y 25 céntimos con el precio medio de la luz. En frío baja a unos 5–8 céntimos."),
              ("¿A qué hora es más barato poner la lavadora?", "Con la tarifa PVPC, en las horas más baratas del día, que suelen ser la madrugada o el mediodía. Puedes verlas en la página del precio de la luz hoy.")]),
    dict(slug="lavavajillas", nombre="Lavavajillas", art="un lavavajillas", icono="🍽️",
         modo="ciclo", kwh=1.0, usos=5,
         uso="5 lavados a la semana en programa normal",
         modelos=[("Programa eco", 0.7), ("Programa normal (55–65 °C)", 1.1), ("Programa intensivo (70 °C)", 1.6)],
         texto="Igual que la lavadora, el lavavajillas gasta sobre todo en calentar el agua. Un lavavajillas lleno usa menos agua y menos energía que fregar la misma vajilla a mano con agua caliente.",
         trucos=["Ponlo solo cuando esté lleno.", "Usa el programa eco: tarda más, pero gasta hasta un 30 % menos.", "No hace falta aclarar los platos con agua caliente antes de meterlos."],
         faq=[("¿Gasta más el lavavajillas o fregar a mano?", "Fregar a mano con agua caliente suele gastar más agua y más energía que un lavavajillas lleno en programa eco."),
              ("¿Cuánto cuesta un lavado del lavavajillas?", "Entre 15 y 35 céntimos según el programa, con el precio medio de la luz.")]),
    dict(slug="microondas", nombre="Microondas", art="un microondas", icono="📡",
         modo="potencia", w=800, horas=0.25, dias=30, factor=1,
         uso="15 minutos al día",
         modelos=[("Microondas pequeño", 700), ("Microondas normal", 900), ("Microondas con grill", 1200)],
         texto="El microondas tiene una potencia alta, pero se usa muy poco tiempo, así que su gasto mensual es pequeño. Para calentar raciones pequeñas es de los aparatos más eficientes de la cocina.",
         trucos=["Para calentar una taza de agua gasta menos que la vitrocerámica.", "Tapa los alimentos: se calientan antes y de forma más uniforme.", "Desenchúfalo si no usas el reloj: el modo espera también consume."],
         faq=[("¿Cuánto gasta un microondas en 1 minuto?", "Unos 0,015 kWh, menos de medio céntimo."),
              ("¿Gasta más el microondas o el horno?", "El horno gasta mucho más: para calentar una ración, el microondas consume unas 10 veces menos.")]),
    dict(slug="televisor", nombre="Televisor", art="un televisor", icono="📺",
         modo="potencia", w=100, horas=4, dias=30, factor=1,
         uso="4 horas al día",
         modelos=[("Televisor LED de 32\"", 40), ("Televisor LED de 55\"", 100), ("Televisor OLED de 65\"", 150), ("Televisor de 75\" o más", 250)],
         texto="El consumo de un televisor depende sobre todo del tamaño de la pantalla y del brillo. Los modos «vívido» o «dinámico» pueden subir el consumo un 30–50 % respecto al modo estándar o eco.",
         trucos=["Usa el modo de imagen eco o estándar.", "Baja el brillo si ves la tele de noche.", "Apágalo del todo o con una regleta si no lo usas en días."],
         faq=[("¿Cuánto gasta un televisor en modo espera?", "Los televisores modernos gastan menos de 0,5 W en espera, unos céntimos al año. Los antiguos podían gastar 5–10 W."),
              ("¿Gasta mucho un televisor encendido todo el día?", "Un televisor de 55\" encendido 12 horas al día gasta unos 36 kWh al mes, alrededor de 8 euros con el precio medio de la luz.")]),
    dict(slug="ordenador", nombre="Ordenador", art="un ordenador", icono="💻",
         modo="potencia", w=150, horas=6, dias=30, factor=1,
         uso="6 horas al día, uso de oficina",
         modelos=[("Portátil", 50), ("Sobremesa de oficina", 120), ("Sobremesa gaming jugando", 450), ("Monitor adicional", 30)],
         texto="Un ordenador de oficina gasta poco, pero uno de gaming con una tarjeta gráfica potente puede consumir 400–600 W mientras juegas. Los portátiles son los más eficientes: gastan entre 3 y 5 veces menos que un sobremesa.",
         trucos=["Activa la suspensión automática tras 15 minutos sin uso.", "Apaga el monitor y los altavoces con una regleta.", "Para tareas sencillas, usa el portátil."],
         faq=[("¿Cuánto gasta un ordenador gaming al mes?", "Jugando 3 horas al día con un equipo de 450 W, unos 40 kWh al mes, alrededor de 9–10 euros."),
              ("¿Gasta más dejar el ordenador en suspensión o apagarlo?", "En suspensión gasta 1–5 W. Si no lo vas a usar en horas, apágalo; para pausas cortas, la suspensión está bien.")]),
    dict(slug="playstation-5", nombre="PlayStation 5", art="una PlayStation 5", icono="🎮",
         modo="potencia", w=200, horas=2, dias=30, factor=1,
         uso="2 horas al día jugando",
         modelos=[("Viendo series o películas", 70), ("Jugando a juegos sencillos", 150), ("Jugando a juegos exigentes", 220)],
         texto="Una consola actual gasta alrededor de 200 W mientras juegas a un juego exigente, más que un televisor. En modo reposo con descarga de juegos activada consume unos pocos vatios todo el día.",
         trucos=["Desactiva el modo reposo con funciones si no descargas juegos: ahorras unos 2–3 € al año.", "Para ver series, la app del televisor gasta menos que la consola."],
         faq=[("¿Cuánto gasta una PS5 en una hora?", "Unos 0,2 kWh jugando, entre 4 y 5 céntimos con el precio medio de la luz."),
              ("¿Gasta más una PS5 o una Xbox Series X?", "Gastan casi lo mismo: unos 200 W jugando. La Xbox Series S gasta alrededor de la mitad.")]),
    dict(slug="calefactor-electrico", meses=5, nombre="Calefactor eléctrico", art="un calefactor eléctrico", icono="♨️",
         modo="potencia", w=2000, horas=3, dias=30, factor=0.8,
         uso="3 horas al día en invierno",
         modelos=[("Calefactor pequeño (posición baja)", 1000), ("Calefactor de 2000 W", 2000), ("Calefactor cerámico de baño", 1500)],
         texto="Un calefactor de aire convierte toda la electricidad en calor, pero no más: 1 kWh de luz da 1 kWh de calor. Calienta rápido una habitación pequeña, pero para calentar varias horas al día sale mucho más caro que una bomba de calor.",
         trucos=["Úsalo solo para calentar rápido un baño o una habitación pequeña.", "Usa el termostato en lugar de dejarlo a máxima potencia.", "Para muchas horas al día, una bomba de calor gasta 3 o 4 veces menos."],
         faq=[("¿Cuánto cuesta tener un calefactor encendido una hora?", "Un calefactor de 2000 W a plena potencia gasta 2 kWh por hora, unos 45–50 céntimos con el precio medio de la luz."),
              ("¿Gasta menos un calefactor cerámico?", "No: todos los calefactores eléctricos dan el mismo calor por kWh. Los cerámicos solo reparten el calor de otra forma.")]),
    dict(slug="aire-acondicionado", meses=4, nombre="Aire acondicionado", art="un aire acondicionado", icono="❄️",
         modo="potencia", w=900, horas=6, dias=30, factor=0.6,
         uso="6 horas al día en verano, equipo de 3.000 frigorías",
         modelos=[("Split de 2.250 frigorías", 700), ("Split de 3.000 frigorías", 900), ("Split de 4.500 frigorías", 1400), ("Aire portátil", 1100)],
         texto="Un aire acondicionado inverter no funciona siempre a su potencia máxima: cuando la habitación llega a la temperatura elegida, el compresor baja de revoluciones. Por eso el consumo real suele ser el 40–70 % de su potencia nominal.",
         trucos=["Pon el termostato a 25–26 °C: cada grado menos sube el consumo un 7 % aproximadamente.", "Cierra persianas y cortinas en las horas de sol.", "Limpia los filtros cada mes en verano."],
         faq=[("¿Cuánto gasta un aire acondicionado al mes?", "Un equipo de 3.000 frigorías usado 6 horas al día gasta unos 100 kWh al mes, alrededor de 20–25 euros con el precio medio de la luz."),
              ("¿Gasta más el aire acondicionado portátil?", "Sí: los portátiles son menos eficientes que los split y gastan entre un 30 y un 50 % más para enfriar lo mismo.")]),
    dict(slug="plancha", nombre="Plancha", art="una plancha", icono="👔",
         modo="potencia", w=2200, horas=1, dias=8, factor=0.5,
         uso="1 hora, 2 veces a la semana",
         modelos=[("Plancha de vapor normal", 2200), ("Plancha con calderín", 2400), ("Plancha de viaje", 1000)],
         texto="La plancha tiene mucha potencia, pero el termostato la apaga y la enciende para mantener la temperatura, así que en una hora de planchado consume alrededor de 1 kWh.",
         trucos=["Plancha mucha ropa de una vez, no prenda a prenda.", "Empieza por la ropa que necesita menos temperatura.", "Desenchúfala unos minutos antes de acabar y aprovecha el calor."],
         faq=[("¿Cuánto cuesta planchar una hora?", "Entre 20 y 30 céntimos con el precio medio de la luz."),
              ("¿Gasta más una plancha con calderín?", "Gasta algo más por hora, pero plancha más rápido, así que para mucha ropa el gasto total es parecido.")]),
    dict(slug="bombilla-led", nombre="Bombilla LED", art="una bombilla LED", icono="💡",
         modo="potencia", w=9, horas=5, dias=30, factor=1,
         uso="5 horas al día",
         modelos=[("LED de 9 W (equivale a 60 W)", 9), ("LED de 14 W (equivale a 100 W)", 14), ("Bombilla incandescente de 60 W", 60), ("Halógena de 50 W", 50)],
         texto="Una bombilla LED da la misma luz que una incandescente gastando 6 o 7 veces menos. Una bombilla LED de 9 W encendida 5 horas al día gasta apenas unos céntimos al mes.",
         trucos=["Cambia primero las bombillas que más horas están encendidas.", "Elige la luz por lúmenes, no por vatios: 800 lúmenes equivalen a una bombilla clásica de 60 W."],
         faq=[("¿Cuánto ahorro cambiando una bombilla a LED?", "Cambiar una incandescente de 60 W por una LED de 9 W, encendida 5 horas al día, ahorra unos 7–8 kWh al mes por bombilla."),
              ("¿Gasta más encender y apagar una bombilla LED?", "No. Encender una LED no tiene ningún pico de consumo apreciable: apágala siempre que salgas de la habitación.")]),
    dict(slug="cafetera", nombre="Cafetera", art="una cafetera", icono="☕",
         modo="ciclo", kwh=0.03, usos=14,
         uso="2 cafés al día con una cafetera de cápsulas",
         modelos=[("Café de cápsulas", 0.03), ("Café de cafetera superautomática", 0.04), ("Jarra de cafetera de goteo", 0.12)],
         texto="Preparar un café gasta muy poco: la cafetera solo calienta el agua durante unos segundos. Lo que más gasta es dejarla encendida: las cafeteras de goteo con placa calefactora pueden consumir 50–80 W mientras mantienen la jarra caliente.",
         trucos=["Activa el apagado automático.", "No dejes la jarra en la placa caliente: mejor un termo.", "Descalcifica la cafetera: la cal hace que gaste más en calentar."],
         faq=[("¿Cuánto cuesta un café de cápsula en luz?", "Menos de un céntimo: unos 0,03 kWh por café."),
              ("¿Gasta mucho una cafetera en espera?", "Las cafeteras modernas se apagan solas; las que no, pueden gastar unos 1–2 W en espera.")]),
    # Invierno
    dict(slug="radiador-de-aceite", meses=5, nombre="Radiador de aceite", art="un radiador de aceite", icono="🛢️",
         modo="potencia", w=2000, horas=4, dias=30, factor=0.6,
         uso="4 horas al día en invierno, con el termostato a media potencia",
         modelos=[("Radiador de 7 elementos (1500 W)", 1500), ("Radiador de 9 elementos (2000 W)", 2000), ("Radiador de 11 elementos (2500 W)", 2500)],
         texto="Un radiador de aceite calienta el aceite de su interior con una resistencia, y el aceite va soltando el calor poco a poco. Tarda más en calentar que un calefactor, pero sigue dando calor un rato después de apagarse. En consumo es igual que cualquier aparato de resistencia: 1 kWh de luz da 1 kWh de calor, ni más ni menos.",
         trucos=["Usa el termostato: a 20–21 °C la resistencia se apaga buena parte del tiempo.", "Apágalo un rato antes de irte de la habitación: el aceite sigue calentando.", "Cierra puertas y ventanas: calienta bien una habitación, no la casa entera.", "Para muchas horas al día, una bomba de calor gasta 3 o 4 veces menos."],
         faq=[("¿Cuánto gasta un radiador de aceite por hora?", "Un radiador de 2000 W a media potencia gasta alrededor de 1,2 kWh por hora, unos 25–30 céntimos con el precio medio actual de la luz. A máxima potencia, el doble."),
              ("¿Gasta menos un radiador de aceite que un calefactor?", "Para dar el mismo calor gastan lo mismo, porque los dos usan una resistencia. La diferencia es que el de aceite reparte el calor de forma más suave y lo mantiene un rato al apagarlo.")]),
    dict(slug="bomba-de-calor", meses=5, nombre="Bomba de calor", art="una bomba de calor", icono="🌡️",
         modo="potencia", w=850, horas=6, dias=30, factor=0.6,
         uso="6 horas al día en invierno, split de 3.000 frigorías en modo calor",
         modelos=[("Split de 2.250 frigorías", 650), ("Split de 3.000 frigorías", 850), ("Split de 4.500 frigorías", 1300), ("Aerotermia para toda la casa", 2500)],
         texto="Una bomba de calor (el aire acondicionado en modo calor) no fabrica el calor con una resistencia: lo saca del aire de fuera y lo mete en casa. Por eso, por cada kWh de luz que gasta, da entre 3 y 4 kWh de calor. Es el sistema de calefacción eléctrica más barato, sobre todo si el equipo es inverter.",
         trucos=["Ponla a 20–21 °C: cada grado más sube el consumo alrededor de un 7 %.", "No la apagues y enciendas a cada rato: el arranque es lo que más gasta.", "Limpia los filtros al empezar el invierno.", "En los días muy fríos rinde algo menos, pero sigue siendo más barata que un radiador."],
         faq=[("¿Cuánto gasta el aire acondicionado en modo calor?", "Un split de 3.000 frigorías usado 6 horas al día gasta unos 90 kWh al mes en invierno, alrededor de 20 euros con el precio medio de la luz."),
              ("¿Es más barata la bomba de calor que un radiador eléctrico?", "Sí: para dar el mismo calor gasta entre 3 y 4 veces menos, porque aprovecha el calor del aire exterior en lugar de producirlo con una resistencia.")]),
    dict(slug="secador-de-pelo", nombre="Secador de pelo", art="un secador de pelo", icono="💨",
         modo="potencia", w=2000, horas=0.15, dias=30, factor=1,
         uso="unos 9 minutos al día a máxima potencia",
         modelos=[("Secador de viaje", 1200), ("Secador normal", 2000), ("Secador profesional", 2400)],
         texto="El secador de pelo es de los aparatos con más potencia de casa, pero se usa muy poco rato. Casi toda la electricidad se va en la resistencia que calienta el aire, así que la posición de aire templado o frío gasta bastante menos que la de máximo calor.",
         trucos=["Quita el exceso de agua con la toalla antes de usar el secador.", "Usa la posición de calor medio: seca casi igual y gasta menos.", "Limpia el filtro de la parte de atrás: si se tapa, tarda más en secar."],
         faq=[("¿Cuánto cuesta secarse el pelo?", "Un secador de 2000 W usado 9 minutos gasta 0,3 kWh, unos 7 céntimos. Al mes, unos 2 euros si lo usas cada día."),
              ("¿Puede saltar la luz con el secador?", "Sí, si a la vez están encendidos el horno, la lavadora o un radiador: el secador suma 2 kW de golpe. Si te pasa a menudo, revisa tu potencia contratada.")]),
    dict(slug="manta-electrica", meses=5, nombre="Manta eléctrica", art="una manta eléctrica", icono="🛏️",
         modo="potencia", w=100, horas=3, dias=30, factor=0.7,
         uso="3 horas al día en el sofá o para calentar la cama",
         modelos=[("Calientacamas bajo el colchón", 60), ("Manta para el sofá", 100), ("Manta grande de matrimonio", 160)],
         texto="Una manta eléctrica gasta muy poco porque calienta tu cuerpo directamente, no el aire de toda la habitación. Su potencia suele estar entre 60 y 160 W, menos que una bombilla antigua, y el termostato baja la potencia cuando ya está caliente.",
         trucos=["Úsala para calentar la cama antes de acostarte y apágala al dormir.", "En el sofá, combínala con la calefacción más baja: cada grado menos de termostato ahorra mucho más.", "Revisa que el cable y el mando estén en buen estado y no la dobles mientras está encendida."],
         faq=[("¿Cuánto cuesta tener una manta eléctrica encendida toda la noche?", "Una manta de 100 W a media potencia gasta unos 0,5 kWh en 8 horas, alrededor de 12 céntimos con el precio medio de la luz."),
              ("¿Gasta menos una manta eléctrica que la calefacción?", "Muchísimo menos: una manta gasta unos 0,07 kWh por hora y un radiador, 1–2 kWh. Compara tu caso en la calculadora de manta eléctrica o calefacción.")]),
    dict(slug="toallero-electrico", meses=6, nombre="Toallero eléctrico", art="un toallero eléctrico", icono="🧻",
         modo="potencia", w=500, horas=2, dias=30, factor=0.8,
         uso="2 horas al día, por la mañana y por la noche",
         modelos=[("Toallero pequeño", 300), ("Toallero mediano", 500), ("Toallero grande", 800)],
         texto="Un toallero eléctrico es un pequeño radiador de resistencia: seca las toallas y calienta un poco el baño. Gasta poco si lo usas un par de horas al día, pero si se queda encendido todo el día puede costar más que una nevera.",
         trucos=["Prográmalo para que se encienda solo antes de la ducha.", "No lo dejes encendido todo el día: con 1–2 horas basta para secar las toallas.", "Si tiene termostato, ponlo a media potencia."],
         faq=[("¿Cuánto gasta un toallero eléctrico encendido todo el día?", "Un toallero de 500 W encendido 24 horas a media potencia gasta unos 9–10 kWh al día, más de 2 euros diarios. Por eso conviene programarlo."),
              ("¿Merece la pena un toallero eléctrico?", "Si lo usas 1–2 horas al día cuesta unos 5 euros al mes, y seca las toallas y templa el baño. Encendido todo el día deja de compensar.")]),
    dict(slug="secadora", nombre="Secadora", art="una secadora", icono="🌀",
         modo="ciclo", kwh=4.0, usos=3,
         uso="3 secados a la semana en una secadora de condensación",
         titulo="¿Cuánto gasta una secadora? Por secado, al mes y al año",
         modelos=[("Bomba de calor (la más eficiente)", 1.6), ("Condensación", 4.0), ("Evacuación (la más antigua)", 4.6)],
         texto="La secadora gasta casi toda la electricidad en calentar el aire que seca la ropa. Las de bomba de calor reciclan ese calor y gastan menos de la mitad que las de condensación o evacuación, aunque tardan un poco más. Lo que más cambia el gasto es lo mojada que entra la ropa: cuanto mejor centrifugada, menos tiempo de secado.",
         trucos=["Centrifuga en la lavadora a 1.200 revoluciones o más antes de secar.", "Llénala, pero sin apretar: la ropa necesita moverse para secarse.", "Limpia el filtro de pelusa después de cada uso y el condensador cada pocas semanas.", "Tiende lo que puedas: un deshumidificador junto al tendedero gasta mucho menos."],
         faq=[("¿Cuánto cuesta poner la secadora una vez?", "Con el precio medio actual de la luz, entre 35 y 45 céntimos en una secadora de bomba de calor y alrededor de 1 euro en una de condensación o evacuación."),
              ("¿Gasta más la secadora o la lavadora?", "La secadora, unas 4 veces más por uso: una lavadora a 40 °C gasta alrededor de 1 kWh y una secadora de condensación, unos 4 kWh."),
              ("¿Merece la pena una secadora de bomba de calor?", "Si secas varias veces por semana, sí: ahorra unos 2,4 kWh en cada secado, que con 3 secados a la semana son más de 80 euros al año con el precio actual de la luz.")]),
    dict(slug="deshumidificador", meses=6, nombre="Deshumidificador", art="un deshumidificador", icono="💧",
         modo="potencia", w=250, horas=8, dias=30, factor=0.7,
         uso="8 horas al día en invierno, con el higrostato al 55 %",
         modelos=[("Compresor de 10 litros al día", 200), ("Compresor de 20 litros al día", 300), ("Desecante de 7 litros al día", 600)],
         texto="Los deshumidificadores de compresor funcionan como una nevera pequeña: enfrían el aire para que el agua se condense. Gastan poco, pero rinden peor con frío. Los de desecante gastan bastante más, pero funcionan mejor en habitaciones frías y además dan algo de calor. Si tiene higrostato, se para cuando llega a la humedad que le marques.",
         trucos=["Pon el higrostato al 50–55 %: más seco no hace falta y gasta más.", "Cierra puertas y ventanas de la habitación mientras funciona.", "Ponlo junto al tendedero: la ropa se seca en horas y gasta mucho menos que una secadora.", "Limpia el filtro cada pocas semanas."],
         faq=[("¿Cuánto gasta un deshumidificador al día?", "Uno de compresor de 250 W encendido 8 horas, con el higrostato parándolo a ratos, gasta unos 1,4 kWh al día: alrededor de 30–35 céntimos con el precio medio de la luz."),
              ("¿Es más barato secar la ropa con un deshumidificador que con la secadora?", "Normalmente sí. Un deshumidificador de compresor junto al tendedero gasta alrededor de 1 kWh en secar una colada, frente a los 4 kWh de una secadora de condensación."),
              ("¿Gasta mucho un deshumidificador de desecante?", "Más que uno de compresor: unos 600 W, casi como un radiador pequeño. A cambio, funciona mejor en habitaciones frías y calienta un poco el ambiente.")]),
    dict(slug="luces-de-navidad", meses=1, nombre="Luces de Navidad", art="las luces de Navidad", icono="🎄",
         verbo="gastan", modo="potencia", w=20, horas=6, dias=30, factor=1,
         uso="6 horas al día durante un mes, con varias tiras LED",
         titulo="¿Cuánto gastan las luces de Navidad? LED y antiguas",
         modelos=[("Una tira LED de 100 luces", 7), ("Varias tiras LED (árbol y balcón)", 20), ("Tira de 100 luces de bombilla antigua", 40), ("Decoración grande de fachada", 150)],
         texto="Las luces LED gastan muy poco: una tira de 100 luces consume unos 5–8 W, menos que una bombilla. Las tiras antiguas de bombillitas incandescentes gastan entre 5 y 8 veces más, y además se calientan. Lo que de verdad sube la factura son las decoraciones grandes de fachada o los proyectores, y dejarlas encendidas toda la noche.",
         trucos=["Usa luces LED: gastan hasta 8 veces menos que las antiguas.", "Ponles un temporizador o un enchufe programable para que se apaguen solas a medianoche.", "Apágalas cuando no haya nadie en casa ni nadie las vea.", "Las de exterior con placa solar no gastan luz de la red."],
         faq=[("¿Cuánto gastan las luces de Navidad al día?", "Una tira LED de 100 luces encendida 6 horas gasta unos 0,04 kWh, menos de un céntimo al día. Una tira antigua de bombillitas, unos 0,24 kWh: alrededor de 5–6 céntimos."),
              ("¿Gastan más las luces de Navidad LED o las antiguas?", "Las antiguas, entre 5 y 8 veces más. Una tira LED de 100 luces consume unos 7 W y una de bombillitas incandescentes, unos 40 W."),
              ("¿Es caro dejar las luces de Navidad encendidas toda la noche?", "Con tiras LED, poco: unos céntimos al día. Con luces antiguas o decoraciones grandes de fachada puede sumar varios euros al mes, así que conviene un temporizador.")]),
    dict(slug="estufa-halogena", meses=5, nombre="Estufa halógena o de cuarzo", art="una estufa halógena", icono="🔆",
         modo="potencia", w=1200, horas=3, dias=30, factor=1,
         uso="3 horas al día con todos los tubos encendidos",
         modelos=[("Un tubo", 400), ("Dos tubos", 800), ("Tres tubos", 1200)],
         texto="Las estufas halógenas y de cuarzo calientan por radiación: dan calor a las personas y objetos que tienen delante, no al aire de la habitación. Por eso notas el calor al momento, pero en cuanto te alejas o la apagas se va. No tienen termostato: gastan toda su potencia mientras están encendidas.",
         trucos=["Úsala para ratos cortos y cerca de ti, por ejemplo en la mesa de trabajo.", "Enciende solo los tubos que necesites.", "Para calentar una habitación varias horas, una bomba de calor gasta mucho menos."],
         titulo="¿Cuánto gasta una estufa halógena? Por hora, al día y al mes",
         horas_tabla=[1, 2, 4, 8],
         comparar=["manta-electrica", "bomba-de-calor", "radiador-de-aceite", "calefactor-electrico"],
         comparar_texto="Por hora, la halógena gasta como un radiador de aceite y más del doble que una bomba de calor. Como no calienta el aire, sale cara para caldear una habitación durante horas; para un rato corto y cerca de ti sí sale a cuenta, porque da calor al momento.",
         faq=[("¿Cuánto gasta una estufa halógena por hora?", "Con tres tubos (1200 W) gasta 1,2 kWh por hora, unos 28 céntimos con el precio medio de la luz. Con un tubo, la tercera parte."),
              ("¿Cuánto gasta una estufa halógena de 1200 W en 8 horas?", "Unos 9,6 kWh: algo más de 2 euros al día con el precio medio de la luz. Si la usas así todo el mes, más de 60 euros."),
              ("¿Se puede dejar una estufa halógena encendida toda la noche?", "No es recomendable. No tiene termostato, así que gasta toda su potencia las 8 horas, y si queda cerca de la cama, la ropa o las cortinas hay riesgo de incendio. Para la noche gasta mucho menos una manta eléctrica."),
              ("¿Qué gasta menos, una estufa halógena o un radiador de aceite?", "Por hora gastan parecido (un radiador de 2000 W con termostato, unos 1,2 kWh de media). Para un rato corto y cerca de ti, mejor la halógena; para calentar la habitación varias horas, el radiador, que guarda el calor."),
              ("¿Gasta menos una estufa de cuarzo, de carbono o halógena?", "Con la misma potencia gastan exactamente lo mismo: 1 kWh por cada hora a 1.000 W. Cambia la forma de dar calor, no el consumo. Fíjate en los vatios de la etiqueta."),
              ("¿Gasta menos una estufa halógena que un calefactor?", "Por hora gasta lo que marque su potencia, igual que un calefactor. Puede salir más barata si la usas poco rato y cerca, porque calienta a la persona y no toda la habitación.")]),
]


def precio_luz():
    try:
        d = json.loads((WEB / "datos" / "luz.json").read_text(encoding="utf-8"))
        return float(d["conImpuestos"]["media"]), d.get("desde"), d.get("hasta")
    except Exception:
        return PRECIO_POR_DEFECTO, None, None


def num(x, dec):
    entero, _, frac = f"{x:,.{dec}f}".partition(".")
    entero = entero.replace(",", ".")
    return entero + ("," + frac if dec else "")


def eur(x):
    return num(x, 2) + " €"


def meses(a):
    """Meses de uso al año: los aparatos de calefacción o aire solo se usan en su temporada."""
    return a.get("meses", 12)


def al_anio(a):
    if meses(a) == 1:
        return "en toda la temporada (un mes)"
    return "al año" if meses(a) == 12 else f"al año ({meses(a)} meses de uso)"


def verbo(a):
    """«gasta» o «gastan» (las luces de Navidad)."""
    return a.get("verbo", "gasta")


def kwh_mes(a):
    if a["modo"] == "ciclo":
        return a["kwh"] * a["usos"] * 52 / 12
    return a["w"] / 1000 * a["horas"] * a["dias"] * a["factor"]


def plantilla_base():
    base = (WEB / "calculadoras" / "coste-viaje-coche.html").read_text(encoding="utf-8")
    head_assets = base[base.index('  <link rel="stylesheet"'):base.index("</head>")]
    header = base[base.index("<body>"):base.index('<main class="container">')]
    i = base.index('<footer class="site-footer">')
    j = base.index("\n", base.index('assets/main.js', i)) + 1
    # El pie de las calculadoras enlaza a otras calculadoras con rutas relativas a calculadoras/
    footer = re.sub(r'href="(?!\.\./|https?:|#|/)([^"]+)"', r'href="../calculadoras/\1"', base[i:j])
    return head_assets, header, footer


def pagina(a, p, otros, base):
    head_assets, header, footer = base
    e = escape
    url = f"{DOMINIO}/{CARPETA}/{a['slug']}"
    mes = kwh_mes(a)
    titulo = a.get("titulo") or f"¿Cuánto {verbo(a)} {a['art']}? Consumo y coste al mes"
    if len(titulo) > 60:
        titulo = f"¿Cuánto {verbo(a)} {a['art']} al mes?"
    desc = (f"{a['nombre']}: unos {num(mes, 0)} kWh y {eur(mes * p)} al mes con un uso normal y el precio actual "
            f"de la luz. Calcula tu gasto según el modelo y las horas de uso.")
    if a["modo"] == "ciclo":
        filas = "".join(f"<tr><td>{e(m)}</td><td class=\"num\">{num(k, 2)} kWh</td><td class=\"num\">{eur(k * p)}</td>"
                        f"<td class=\"num\">{eur(k * a['usos'] * 52 / 12 * p)}</td></tr>" for m, k in a["modelos"])
        cab = "<th>Uso</th><th class=\"num\">Consumo por uso</th><th class=\"num\">Coste por uso</th><th class=\"num\">Al mes*</th>"
        nota_tabla = f"* Con {a['usos']} usos a la semana."
        formula = (f"<p class=\"note\"><strong>Coste al mes = kWh por uso × usos a la semana × 52 ÷ 12 × precio del kWh</strong></p>"
                   f"<p><strong>Ejemplo:</strong> {num(a['kwh'], 2)} kWh × {a['usos']} usos × 52 ÷ 12 = {num(mes, 1)} kWh al mes. "
                   f"A {num(p, 3)} €/kWh son <strong>{eur(mes * p)} al mes</strong>.</p>")
        campos = f"""        <div class="row">
          <div class="field">
            <label for="kwh">Consumo por uso (kWh)</label>
            <input id="kwh" type="number" min="0" step="0.01" value="{a['kwh']}" inputmode="decimal">
            <small>Viene en la etiqueta energética o en el manual.</small>
          </div>
          <div class="field">
            <label for="usos">Usos a la semana</label>
            <input id="usos" type="number" min="0" step="1" value="{a['usos']}" inputmode="numeric">
          </div>
        </div>"""
        js_kwh = "var kwhMes = num('kwh') * num('usos') * 52 / 12;"
    else:
        filas = "".join(f"<tr><td>{e(m)}</td><td class=\"num\">{num(w, 0)} W</td><td class=\"num\">{eur(w / 1000 * a['factor'] * p)}</td>"
                        f"<td class=\"num\">{eur(w / 1000 * a['factor'] * a['horas'] * a['dias'] * p)}</td></tr>" for m, w in a["modelos"])
        cab = "<th>Modelo o uso</th><th class=\"num\">Potencia</th><th class=\"num\">Coste por hora</th><th class=\"num\">Al mes*</th>"
        nota_tabla = f"* Con un uso de {e(a['uso'])}."
        factor_txt = (f" × {num(a['factor'] * 100, 0)} % del tiempo a plena potencia" if a["factor"] < 1 else "")
        formula = (f"<p class=\"note\"><strong>Consumo (kWh) = potencia (W) ÷ 1.000 × horas de uso{e(factor_txt)}</strong><br>"
                   f"<strong>Coste = consumo × precio del kWh</strong></p>"
                   f"<p><strong>Ejemplo:</strong> {num(a['w'], 0)} W ÷ 1.000 × {num(a['horas'], 2)} h × {a['dias']} días"
                   f"{e(factor_txt)} = {num(mes, 1)} kWh al mes. A {num(p, 3)} €/kWh son <strong>{eur(mes * p)} al mes</strong>.</p>")
        campos = f"""        <div class="row">
          <div class="field">
            <label for="w">Potencia (W)</label>
            <input id="w" type="number" min="0" step="10" value="{a['w']}" inputmode="decimal">
            <small>Viene en la etiqueta del aparato o en el manual.</small>
          </div>
          <div class="field">
            <label for="horas">Horas de uso al día</label>
            <input id="horas" type="number" min="0" step="0.25" value="{a['horas']}" inputmode="decimal">
          </div>
        </div>
        <div class="row">
          <div class="field">
            <label for="dias">Días de uso al mes</label>
            <input id="dias" type="number" min="0" max="31" step="1" value="{a['dias']}" inputmode="numeric">
          </div>
          <div class="field">
            <label for="factor">Tiempo a plena potencia (%)</label>
            <input id="factor" type="number" min="1" max="100" step="5" value="{round(a['factor'] * 100)}" inputmode="numeric">
            <small>{'El termostato apaga y enciende el aparato: no gasta su potencia máxima todo el rato.' if a['factor'] < 1 else 'Este aparato funciona a su potencia todo el tiempo de uso.'}</small>
          </div>
        </div>"""
        js_kwh = "var kwhMes = num('w') / 1000 * num('horas') * num('dias') * num('factor') / 100;"

    ld = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": titulo, "url": url, "inLanguage": "es-ES",
         "dateModified": date.today().isoformat(), "author": {"@type": "Person", "name": "Albert Sanchez Guiu"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMINIO}/"},
            {"@type": "ListItem", "position": 2, "name": "Consumo de electrodomésticos", "item": f"{DOMINIO}/consumo-electrodomesticos"},
            {"@type": "ListItem", "position": 3, "name": a["nombre"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in a["faq"]]},
    ]
    extra = ""
    if a.get("horas_tabla"):
        cab_h = "".join(f"<th class=\"num\">{e(m)}</th>" for m, _ in a["modelos"])
        filas_h = "".join(f"<tr><td>{h} {'hora' if h == 1 else 'horas'}</td>"
                          + "".join(f"<td class=\"num\">{eur(w / 1000 * a['factor'] * h * p)}</td>" for _, w in a["modelos"])
                          + "</tr>" for h in a["horas_tabla"])
        extra += (f"\n        <h2>Cuánto {verbo(a)} {e(a['art'])} al día</h2>\n"
                  f"        <div class=\"table-wrap\"><table class=\"data\"><thead><tr><th>Encendida al día</th>{cab_h}</tr></thead><tbody>{filas_h}</tbody></table></div>\n"
                  f"        <p>Coste de un día de uso con el precio medio de la luz ({num(p, 3)} €/kWh). Para saber el gasto del mes, multiplica por los días que la enciendas.</p>\n")
    if a.get("comparar"):
        por_slug = {o["slug"]: o for o in APARATOS}
        comp = [a] + [por_slug[s] for s in a["comparar"]]
        comp.sort(key=lambda o: o["w"] * o["factor"])
        def celda(o):
            return e(o["nombre"]) if o is a else f'<a href="{o["slug"]}">{e(o["nombre"])}</a>'
        filas_c = "".join(f"<tr><td>{celda(o)}</td><td class=\"num\">{num(o['w'] * o['factor'] / 1000, 2)} kWh</td>"
                          f"<td class=\"num\">{eur(o['w'] / 1000 * o['factor'] * p)}</td></tr>" for o in comp)
        extra += (f"\n        <h2>Comparada con otras calefacciones</h2>\n"
                  f"        <div class=\"table-wrap\"><table class=\"data\"><thead><tr><th>Aparato</th><th class=\"num\">Consumo por hora</th><th class=\"num\">Coste por hora</th></tr></thead><tbody>{filas_c}</tbody></table></div>\n"
                  f"        <p>Con la potencia y el uso normal de cada aparato. {e(a['comparar_texto'])} "
                  f"Si dudas entre gas y electricidad, compara con la <a href=\"../calculadoras/estufa-butano-o-electrica\">calculadora de estufa de butano o eléctrica</a>.</p>\n")
    faq = "\n".join(f"        <details>\n          <summary>{e(q)}</summary>\n          <p>{e(r)}</p>\n        </details>" for q, r in a["faq"])
    trucos = "".join(f"<li>{e(t)}</li>" for t in a["trucos"])
    rel = "\n".join(f'          <li><a href="{o["slug"]}">{o["icono"]} {e(o["nombre"])}</a></li>' for o in otros)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#1f7a55">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ahorrómetro">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{e(titulo)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://ahorrometro.es/assets/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {json.dumps(ld, ensure_ascii=False)}
  </script>
{head_assets}</head>
<!-- Página generada automáticamente por scripts/paginas_consumo.py: no la edites a mano. -->
{header}<main class="container">
  <nav class="breadcrumbs"><a href="../">Inicio</a> › <a href="../consumo-electrodomesticos">Consumo de electrodomésticos</a> › {e(a['nombre'])}</nav>
  <div class="layout">
    <article>
      <h1>¿Cuánto {verbo(a)} {e(a['art'])}?</h1>
      <p class="lead">Con un uso normal ({e(a['uso'])}), {e(a['art'])} {verbo(a)} unos <strong>{num(mes, 0)} kWh al mes</strong>, es decir, <strong>{eur(mes * p)} al mes</strong>{"" if meses(a) == 1 else f" y {eur(mes * p * meses(a))} {al_anio(a)}"} con el precio medio actual de la luz ({num(p, 3)} €/kWh con impuestos).</p>
      <p class="updated">Por Albert Sanchez · Precio de la luz actualizado automáticamente con datos de Red Eléctrica</p>

      <div class="calc">
{campos}
        <div class="row">
          <div class="field">
            <label for="p">Precio de la luz (€/kWh)</label>
            <input id="p" data-precio="luz" type="number" min="0" step="0.001" value="{p}" inputmode="decimal">
          </div>
        </div>
        <button class="btn" id="calcular">Calcular gasto</button>
        <div class="result" id="res" aria-live="polite"></div>
      </div>


      <div class="content">
        <h2>Consumo de {e(a['art'])} según el modelo</h2>
        <div class="table-wrap"><table class="data"><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>
        <p>{nota_tabla} Precio de la luz: {num(p, 3)} €/kWh, media del PVPC de las últimas 4 semanas con impuestos.</p>

        <h2>Por qué {verbo(a)} lo que {verbo(a)}</h2>
        <p>{e(a['texto'])}</p>
{extra}
        <h2>Cómo calcular el consumo</h2>
        {formula}

        <h2>Trucos para que gaste menos</h2>
        <ul>{trucos}</ul>
        <p>Si tienes la tarifa PVPC, usar los aparatos que más gastan en las horas baratas también reduce la factura: consulta el <a href="../precio-luz-hoy">precio de la luz hoy por horas</a>.</p>

        <h2>Preguntas frecuentes</h2>
{faq}
      </div>
    </article>

    <aside class="sidebar">
      <div class="side-box">
        <h3>¿Cuánto gasta…?</h3>
        <ul>
{rel}
          <li><a href="../consumo-electrodomesticos">📋 Todos los electrodomésticos</a></li>
        </ul>
      </div>
    </aside>
  </div>
</main>

{footer}<script>
(function () {{
  function calcular(scroll) {{
    {js_kwh}
    var p = num('p');
    if (!(kwhMes >= 0 && p >= 0)) {{ showResult('res', '<p>Revisa los datos: todos deben ser números positivos.</p>'); return; }}
    var html = '<div>Te cuesta al mes</div><div class="big">' + eur(kwhMes * p) + '</div>' +
      '<div class="stats">' +
        '<div class="stat"><b>' + eur(kwhMes * p * {meses(a)}) + '</b><span>{al_anio(a)}</span></div>' +
        '<div class="stat"><b>' + fmt(kwhMes, 1) + ' kWh</b><span>al mes</span></div>' +
      '</div>';
    if (scroll) showResult('res', html);
    else {{ var r = document.getElementById('res'); r.innerHTML = html; r.classList.add('show'); }}
  }}
  document.getElementById('calcular').addEventListener('click', function () {{ calcular(true); }});
  document.querySelectorAll('.calc input').forEach(function (el) {{ el.addEventListener('input', function () {{ calcular(false); }}); }});
  calcular(false);
}})();
</script>
</body>
</html>
"""


def indice(p, desde, hasta, base):
    head_assets, header, footer = base
    head_assets = head_assets.replace("../", "")
    header = header.replace('href="../#', 'href="./#').replace('href="../"', 'href="./"').replace('href="../', 'href="')
    footer = footer.replace('href="../', 'href="').replace('src="../', 'src="')
    url = f"{DOMINIO}/consumo-electrodomesticos"
    orden = sorted(APARATOS, key=lambda a: -kwh_mes(a))
    filas = "".join(
        f'<tr><td><a href="{CARPETA}/{a["slug"]}">{a["icono"]} {escape(a["nombre"])}</a><span class="sub">{escape(a["uso"])}</span></td>'
        f'<td class="num">{num(kwh_mes(a), 1)} kWh</td><td class="num">{eur(kwh_mes(a) * p)}</td><td class="num">{eur(kwh_mes(a) * p * meses(a))}{"*" if meses(a) != 12 else ""}</td></tr>'
        for a in orden)
    periodo = f" entre el {desde} y el {hasta}" if desde and hasta else ""
    titulo = "Consumo de electrodomésticos: cuánto gasta cada uno al mes"
    desc = "Tabla del consumo y el coste al mes de cada electrodoméstico con el precio actual de la luz: horno, lavadora, inducción, aire acondicionado, televisor y más."
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMINIO}/"},
        {"@type": "ListItem", "position": 2, "name": "Consumo de electrodomésticos", "item": url}]}]
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{titulo}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#1f7a55">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ahorrómetro">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{titulo}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://ahorrometro.es/assets/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {json.dumps(ld, ensure_ascii=False)}
  </script>
{head_assets}</head>
<!-- Página generada automáticamente por scripts/paginas_consumo.py: no la edites a mano. -->
{header}<main class="container">
  <nav class="breadcrumbs"><a href="./">Inicio</a> › Consumo de electrodomésticos</nav>
  <h1>¿Cuánto gasta cada electrodoméstico?</h1>
  <p class="lead">Consumo y coste al mes de los electrodomésticos más habituales con un uso normal y el precio medio actual de la luz: <strong>{num(p, 3)} €/kWh</strong> con impuestos (PVPC de Red Eléctrica{periodo}).</p>
  <p class="updated">Se actualiza automáticamente cuando cambia el precio de la luz.</p>
  <div class="table-wrap"><table class="data"><thead><tr><th>Electrodoméstico y uso</th><th class="num">Consumo al mes</th><th class="num">Coste al mes</th><th class="num">Al año</th></tr></thead><tbody>{filas}</tbody></table></div>
  <p>* Aparatos de temporada: el coste al año cuenta solo los meses de invierno o de verano en que se usan.</p>
  <p>Pulsa en cada aparato para calcular su gasto con tu modelo y tus horas de uso. Si no está en la lista, usa la <a href="calculadoras/consumo-electrico">calculadora de consumo eléctrico</a> con la potencia de tu aparato.</p>


  <div class="content">
    <h2>Otros aparatos que gastan mucho</h2>
    <ul>
      <li><a href="calculadoras/termo-electrico">Termo eléctrico</a></li>
      <li><a href="calculadoras/frigorifico">Frigorífico</a></li>
      <li><a href="calculadoras/secadora-o-tender">Secadora</a></li>
      <li><a href="calculadoras/radiador-electrico">Radiador eléctrico</a></li>
      <li><a href="calculadoras/freidora-de-aire">Freidora de aire</a></li>
      <li><a href="calculadoras/deshumidificador">Deshumidificador</a></li>
      <li><a href="calculadoras/cargar-coche-electrico">Cargar un coche eléctrico</a></li>
    </ul>
    <h2>Cómo reducir el consumo de tus electrodomésticos</h2>
    <p>Los aparatos que calientan (horno, termo, secadora, calefactores, placas) son los que más gastan. Usarlos menos tiempo o a menor temperatura es lo que más se nota en la factura. Con la tarifa PVPC, ponerlos en las <a href="precio-luz-hoy">horas más baratas del día</a> ahorra todavía más. Y no olvides el <a href="calculadoras/consumo-fantasma">consumo fantasma</a> de los aparatos en espera.</p>
  </div>
</main>

{footer}</body>
</html>
"""


def reemplazar_bloque(ruta, contenido, marca="CONSUMO"):
    texto = ruta.read_text(encoding="utf-8")
    nuevo, n = re.subn(rf"(<!-- {marca}:INICIO -->).*?(<!-- {marca}:FIN -->)",
                       lambda m: m[1] + contenido + m[2], texto, flags=re.S)
    if n != 1:
        raise SystemExit(f"No encuentro los marcadores {marca} en {ruta}")
    if nuevo != texto:
        ruta.write_text(nuevo, encoding="utf-8")


# Aparatos de la tabla de la calculadora de consumo eléctrico
EN_CALCULADORA = ["aire-acondicionado", "calefactor-electrico", "radiador-de-aceite", "placa-de-induccion",
                  "horno-electrico", "lavadora", "lavavajillas", "ordenador", "televisor"]


def bloque_calculadora(p):
    """Ejemplo y tablas de calculadoras/consumo-electrico.html con el precio actual de la luz."""
    filas_w = "".join(f"<tr><td>{num(w, 0)} W</td><td class=\"num\">{num(w / 1000, 2)} kWh</td><td class=\"num\">{eur(w / 1000 * p)}</td>"
                      f"<td class=\"num\">{eur(w / 1000 * 30 * p)}</td></tr>" for w in (100, 500, 1000, 1500, 2000, 3000))
    por_slug = {a["slug"]: a for a in APARATOS}
    filas_a = "".join(f'<tr><td><a href="../{CARPETA}/{a["slug"]}">{escape(a["nombre"])}</a><span class="sub">{escape(a["uso"])}</span></td>'
                      f'<td class="num">{num(kwh_mes(a), 1)} kWh</td><td class="num">{eur(kwh_mes(a) * p)}</td></tr>'
                      for a in sorted((por_slug[s] for s in EN_CALCULADORA), key=lambda a: -kwh_mes(a)))
    return f"""
        <p>Por ejemplo, un radiador de 2000 W encendido 5 horas al día consume 2000 × 5 ÷ 1000 = 10 kWh diarios. A {num(p, 3)} €/kWh son {eur(10 * p)} al día, unos <strong>{eur(300 * p)} al mes</strong> solo por ese aparato.</p>

        <h2>De vatios a euros: cuánto cuesta cada potencia</h2>
        <div class="table-wrap"><table class="data"><thead><tr><th>Potencia</th><th class="num">Consumo por hora</th><th class="num">Coste por hora</th><th class="num">1 h al día durante un mes</th></tr></thead><tbody>{filas_w}</tbody></table></div>
        <p>A toda potencia. Si el aparato tiene termostato (radiadores, aire acondicionado, frigorífico), gasta menos porque se apaga y se enciende.</p>

        <h2>Consumo de los electrodomésticos más comunes</h2>
        <div class="table-wrap"><table class="data"><thead><tr><th>Aparato y uso</th><th class="num">Al mes</th><th class="num">Coste al mes</th></tr></thead><tbody>{filas_a}</tbody></table></div>
        <p>Precio de la luz: {num(p, 3)} €/kWh, media del PVPC de las últimas 4 semanas con impuestos. Lo actualizamos cada día. Mira <a href="../consumo-electrodomesticos">todos los electrodomésticos</a>.</p>
        """


def main():
    p, desde, hasta = precio_luz()
    base = plantilla_base()
    carpeta = WEB / CARPETA
    carpeta.mkdir(exist_ok=True)
    for i, a in enumerate(APARATOS):
        otros = [APARATOS[(i + k) % len(APARATOS)] for k in range(1, 6)]
        (carpeta / f"{a['slug']}.html").write_text(pagina(a, p, otros, base), encoding="utf-8")
    (WEB / "consumo-electrodomesticos.html").write_text(indice(p, desde, hasta, base), encoding="utf-8")
    hoy = date.today().isoformat()
    urls = [f"  <url><loc>{DOMINIO}/consumo-electrodomesticos</loc><lastmod>{hoy}</lastmod><priority>0.9</priority></url>"]
    urls += [f"  <url><loc>{DOMINIO}/{CARPETA}/{a['slug']}</loc><lastmod>{hoy}</lastmod><priority>0.8</priority></url>" for a in APARATOS]
    reemplazar_bloque(WEB / "sitemap.xml", "\n" + "\n".join(urls) + "\n  ")
    calc = WEB / "calculadoras" / "consumo-electrico.html"
    reemplazar_bloque(calc, bloque_calculadora(p), "CONSUMO-CALC")
    texto = calc.read_text(encoding="utf-8")
    nuevo = re.sub(r'(<input id="p" data-precio="luz"[^>]*? value=")[^"]*"', rf'\g<1>{p}"', texto)
    if nuevo != texto:
        calc.write_text(nuevo, encoding="utf-8")
    print(f"{len(APARATOS)} páginas de consumo con la luz a {p} €/kWh")


if __name__ == "__main__":
    main()
