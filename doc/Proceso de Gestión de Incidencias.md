# Proceso de Gestión de Incidencias

## ¿Qué es una incidencia?

La definición de incidencia va a variar en función del tipo que se detecte, aunque esto lo comentaremos más adelante. En reglas generales, una incidencia va a tratar de cualquier evento o situación que afecta negativamente al desarrollo, implementación o funcionamiento del software y que requiere atención para su resolución.

## Tipos de incidencia

En nuestro proyecto, vamos a distinguir 3 tipos de incidencias:

- **Tipo incremento:** Estas incidencias no van a tratarse tanto de problemas en sí, sino de los diferentes incrementos funcionales que van a tratarse durante el desarrollo del proyecto.
  - Ejemplo: Se va a implementar la funcionalidad de implementar censo por excel. Una vez se vaya a realizar, se deberá de crear una incidencia por cada módulo de django que toque ese incremento (Incremento-Censo_por_excel(Booth)).

- **Tipo error:** Estas se tratan de incidencias que no tienen que ver con el código, sino por el proyecto en sí. Por norma general, estas incidencias tendrán unos pasos en concreto para solucionarlas, los que deberán ser comentados en la incidencia.
  - Ejemplo: (Error-Despliegue_Docker)

- **Tipo bug:** Estas serán detectadas cuando, una vez mergeados los cambios a la rama principal, se encuentre algún bug en esta.
  - Ejemplo: (Bug-XXXXX)

Todas estas incidencias deberán ser clasificadas a la hora de encontrarlas en diferentes prioridades (baja, media y alta) en función de la importancia que tenga solucionarla en un breve periodo de tiempo.

## Método de resolución de incidencia

A la hora de resolver una incidencia, esta pasará por 3 estados diferentes: Detectada, En Resolución y Cerrada. Para esto, haremos uso de GitHub Project, siendo cada columna de este el estado de una incidencia, y las diferentes issues se tratarán de incidencias. Una vez añadida esta, se le pondrá una task para el tipo de incidencia que es, otra para la prioridad, y por último se asignará al que le corresponda. Cada tipo de incidencia tendrá diferentes pasos a la hora de solucionarlas:

### Incremento:

1. Análisis de módulos que toca el incremento.
2. Creación de las distintas incidencias.
3. Una vez comenzada la funcionalidad, pasar estas a En Resolución.
4. Añadir pequeñas descripciones respecto a que afecta en la propia incidencia.
5. Al mergear a la rama principal, pasar incidencia a Cerrada.


### Error:

1. Detectar el error.
2. Crear la incidencia, con una explicación paso por paso para solucionar este error.
3. Esta se mantiene en detectada.

### Bug:

1. Detectar el bug.
2. Crear la incidencia.
3. Crear una rama hotfix para solucionar este. Una vez comenzada la resolución, pasar incidencia a En Proceso.
4. Tras mergear la solución del bug, pasar la incidencia a Cerrada.
