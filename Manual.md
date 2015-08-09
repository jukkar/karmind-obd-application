`[English]`

# Introduction #

A quick-guide for the app will be described below.

**Provided with autoinstall, this GUI application allows through OBD (On Board Diagnostics) interface perform checking, clearing and sampling of a few electronic parameters in a given vehicle. With logging features included, output files of any action previously executed may be uploaded to your personal space in [karmind.com](http://www.karmind.com) in order to have it stored and get it reviewed at any time.**

**As interface between this software and the vehicle, an ELM327 controller is needed. It may be purchased in many online stores on the Internet. Only USB cable model has been tested successfully.**

**SO supported: Windows, Unix.**

For further information about what we are working on currently, check [karmind.com](http://www.karmind.com).

_**Disclaimer** This is free software. If source code is not modified, there is no way at all of leading to harm a vehicle. Anyway, there is absolutely no warranty for any action performed by the user of the provided software._

# Details #

Let´s go step by step.

**_SVN checkout_**
  * Perform a checkout from the SVN in Downloads tab, in order to install the app.

**_Installation_**
  * No prerequisites needed. [Further information about setup](https://code.google.com/p/karmind-obd-application/wiki/Installation).

**_Execute application_**
  * Assuming you have followed the instructions above, the karmind app is already installed in your computer, on the location you selected during the installation process. Thus, you may launch the app from your start menu, browsing to the karmind app and clicking on the executable.

  * At this point, Karmind app GUI raises, with its three available options. Before executing any task, following requirements are needed:
  1. The ELM327 unit you will use with Karmind software altogheter, must have been installed and tested previously in the same computer as Karmind app.
  1. The ELM 327 hardware has to be connected in both sides, the vehicle and the computer.
  1. For some car brands, the car engine must be started.

> _Not following earlier requirements will lead to Karmind app malfunction and even crash._

**_App modes_**
> Karmind application allows to execute three different modes to extract information from your vehicle through the OBD interface. In case you are interested in getting deeper knowledge about the basics of On Board Diagnostics protocols, take a look at ISO-15031-5 and ISO-15031-6 international standards.
> While executing any mode, an output file is generated and saved to disk, so as to upload it afterwards to your private space on [karmind.com](http://www.karmind.com). Available modes are described hereafter.

_Check_
  * In a minute, the app get a snapshot of most common Parameter IDs (PIDs) of your vehicle, including invocation of service modes $03 and $07 (pending and stored Diagnostic Trouble Codes, DTCs), so as to look for any issue regarding electronics.
> After getting the info, it may be uploaded to your personal space on [karmind.com](http://www.karmind.com), to have it stored and look trough any DTC may raise thanks to Karmind DTC lookup facilitie.

_Delete_
  * If any issue detected in previous mode causing the Malfunction Indicator Lamp (MIL) to switch on, or any other DTC present, it may be cleaned invoking this operation mode. Take into account that if any issue were the reason for DTCs to raise, it must be fixed or DTCs will show up again later.
> Of course, this action is recorded into a file as well and may be stored on your personal space on [karmind.com](http://www.karmind.com).

_Sampler_
  * This mode allows to sample some cool electronic parameters, such as RPM, throttle position, speed and others while driving. After getting that, the data may be uploaded to your personal space on [karmind.com](http://www.karmind.com), to have it stored and plot some awesome performance graphics.


**_Tips_**

If the app is not able to open the connection with the car through ELM-327, perhaps the polling method to get the ELM port is not working properly on your device. If so, set the variable comport in the elm section of the file karmind.ini (located on the installation path) to the appropriate value.

The application has a logging feature. To enable it, go to karmind.ini file on the installation path, and set the variable event\_log to ON in logging section. A new logging file will be generated with each new inspection.


---


_Be aware of the fact that this app was made with extremely limited resources, and therefore could only be checked against a few brand cars. Thus, it is quite likely to fail while testing against some kind of vehicles._

_Any doubt, improvement or bug to report, let us know, please, hereby or at [karmind.com](http://www.karmind.com). We will be pleased of hearing from you._

Good day!


---


`[Español]`

# Introducción #

A continuación se incluye una guía rápida para la aplicación.

**De instalación automática, esta aplicación GUI permite a través de la interfaz OBD (On Board Diagnostics), realizar la comprobación, borrado y muestreo de los parámetros electrónicos de un vehículo. Con logging incluido, los archivos de salida de cualquier acción ejecutada con anterioridad pueden almacenarse en tu espacio personal en [karmind.com](http://www.karmind.com) con el fin de tenerlos guardados y poder revisarlos en cualquier momento.**

**Como interfaz entre el software y el vehículo, es necesario un cable con controlador ELM327. Se pueden comprar en muchas tiendas online en Internet. El modelo USB ha sido el que se ha probado con éxito.**

**SO soportados: Windows, Lunix.**

Para más información sobre en qué estamos trabajando en la actualidad, visita [karmind.com](http://www.karmind.com).

**_Advertencia_** : Este es software libre. Si el código fuente no se modifica, no hay ninguna posibilidad de causar daños en un vehículo. De todos modos, no hay absolutamente ninguna garantía, por cualquier acción realizada por el usuario del software.

# Detalles #

Vayamos paso a paso.

**_Descarga de la aplicación_**
  * Descarga en fichero de instalación en la pestaña Downloads.

**_Instalación_**
  * No hay requisitos previos necesarios. [Detalles de instalación](http://code.google.com/p/karmind-obd-application/wiki/Installation).

**_Ejecución_**
  * Suponiendo que has seguido las instrucciones anteriores, la aplicación karmind ya está instalado en tu ordenador, en la ubicación que has seleccionado durante el proceso de instalación. Por lo tanto, puedes lanzar la aplicación desde el menú de inicio, navegando hasta la aplicación karmind y haciendo clic en el ejecutable.

  * En este punto, se lanza la aplicación Karmind, con sus tres opciones disponibles. Antes de ejecutar cualquier tarea, se necesitan los siguientes requisitos:
  1. La unidad ELM327 que vas a utilizar con el software Karmind, debe haber sido instalado y probado previamente en el mismo equipo que la aplicación Karmind.
  1. El ELM 327 tiene que estar conectado en ambos extremos (el vehículo y el ordenador).
  1. Para algunas marcas de coches, el motor del coche debe ser arrancado.

> _No obedecer los requisitos anteriores dará lugar a un mal funcionamiento de la aplicación Karmind._

**_Modos de la aplicación_**
> La aplicación Karmind permite ejecutar tres modos diferentes para extraer información del vehículo a través de la interfaz OBD. En caso de estar interesado en obtener un conocimiento más profundo sobre los fundamentos de los protocolos de diagnóstico a bordo, echar un vistazo a las normas internacionales ISO-15031-5 e ISO-15031-6.
> Tras la ejecución de cualquier modo, un archivo de salida se genera y se guarda en disco, para después poder subirlo a tu espacio privado en [karmind.com](http://www.karmind.com). Los modos disponibles se describen a continuación.

_Comprobación (Check)_
  * En aprox. un minuto, la aplicación obtiene una instantánea de los parámetros identificadores más comunes (PID) de tu vehículo, incluyendo la invocación de los modos de servicio de $03 y $07 (muestra los códigos de diagnóstico de problemas, DTC, pendientes y almacenados), con el fin de buscar cualquier cuestión relativa a problemas en la electrónica.
> Después de conseguir la información, puede ser subida a tu espacio personal en [karmind.com](http://www.karmind.com), para tenerla almacenada y poder buscar el significado de cualquier DTC que aparezca en tu coche en el apartado DTCs de la web.

_Borrado (Delete)_
  * En caso de cualquier problema detectado en el modo anterior que haya provocado que la Lámpara Indicadora de Fallo (MIL) se encienda, o cualquier otro DTC que no haya provocado este efecto, se puede invocar la limpieza de errores y testigos mediante este modo de funcionamiento. Ten en cuenta que si había alguna problema para que apareciesen DTCs, y no se solventa, aunque se borren volverán a aparecer.
> Por supuesto, esta acción se registra en un archivo, y también se puede almacenar en tu espacio personal en [karmind.com](http://www.karmind.com).

_Muestreo (Sampler)_
  * Este modo permite muestrear parámetros en ruta, tales como RPM, posición del acelerador, velocidad y otros, durante la conducción. Después estos datos pueden ser cargados en tu espacio personal en [karmind.com](http://www.karmind.com), para almacenarlos y obtener una serie de gráficas de rendimiento.


**_Consejos_**

Si la aplicación no es capaz de abrir la conexión con el coche a través de ELM-327, tal vez el método de sondeo para obtener el puerto ELM no funciona correctamente en el dispositivo. Si es así, establece la variable comport en la sección elm del archivo karmind.ini (situado en la ruta de instalación) al valor adecuado.

La aplicación tiene una función de logging. Para activarla, ve al archivo karmind.ini en la ruta de instalación, y establecer la variable de event\_log en ON en la sección de registro. Un nuevo archivo de registro se genera con cada nueva inspección.


---


_Sé consciente del hecho de que esta aplicación se realizó con recursos muy limitados, por lo que sólo puedo ser probada contra unas pocas marca de coches. Por lo tanto, es muy probable que falle durante su uso en algunas otras._

_Cualquier duda, mejora o error que detectes, háznoslo saber, por favor, por este medio o en [karmind.com](http://www.karmind.com). Estaremos encantados de escucharte._

Buen día!