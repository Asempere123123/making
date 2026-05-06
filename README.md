# Making
El Codigo del proyecto

## Estructura
- actuador.ino -> codigo del micro que controla el servo y tiene uno de los 2 sensores de distancia
- sensor.ino -> codigo del otro micro, que tiene el otro sensor de distancia y un sensor de luz

## Estructura de la parte web (App y esas cosas)
- docker-compose y dockerfiles -> la tengo desplegada a aws con docker, define la estructura de que prodesos tiene que iniciar el servidor para encender todo esto
- backend -> la logica del backend, tiene una app de python con fastapi que guarda los datos en un sqlite
- frontend -> el frontend a compilar. hecho en react

## DND ESTA
Todo esta hosteado en `ddns.asempere.net`, en el puerto 80 la app y el backend en el 8000. Ten en cuenta que no tiene ssl asi q solo te puedes meter por http (no https).
Y ademas al estar en el puerto 8000 NO va con eduroam. [http://ddns.asempere.net/](web). Ademas tiene las meta tags para que se pueda añadir como webapp en el movil, asi que en teoria si la abres en saphari en iphone o en chrome en android (no he probado en android) puedes darle a que la añada como aplicacion a la pantalla de inicio. Sino hay muchas formas de convertir una aplicacion web a nativa. La mas facil seria meterla en un webview del appinventor o sino habra que embeberla en un webview del motor que se este utilizando.
