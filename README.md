# Analizador Léxico - Tarea 2: Teoría de la Computación

Este repositorio contiene el código fuente de un analizador léxico (lexer) desarrollado en Python para la Tarea 2 del curso de Teoría de la Computación. El script `codigo.py` toma un archivo de texto con código fuente de un lenguaje simple estilo C y lo descompone en una secuencia de tokens, imprimiendo el resultado en la consola.

## Requisitos

- Python 3.x

## Uso

Para ejecutar el analizador léxico, sigue estos pasos:

1.  **Clona o descarga el repositorio.** Asegúrate de tener el archivo `codigo.py` y, opcionalmente, el archivo de prueba `demo.txt`.

2.  **Prepara tu archivo de entrada.** Crea un archivo de texto (por ejemplo, `mi_codigo.txt`) con el código fuente que deseas analizar. Puedes usar el archivo `demo.txt` incluido como referencia.

3.  **Ejecuta el script desde la terminal.** Abre una terminal o línea de comandos, navega hasta el directorio donde se encuentra el script y ejecútalo pasando como argumento la ruta al archivo de texto.

    La sintaxis del comando es la siguiente:
    ```bash
    python codigo.py <ruta_al_archivo_de_entrada.txt>
    ```

## Ejemplo de Ejecución

Supongamos que tienes un archivo llamado `demo.txt` con el siguiente contenido:

```c
int x = 42;
x += 1;
if (x >= 10 && x != 13) { // comentario
    x++;
}
```

Para analizar este archivo, ejecutarías el siguiente comando en tu terminal:

```bash
python codigo.py demo.txt
```

La salida producida en la consola será una traza detallada de cada token reconocido, similar a esta:

```
KW_INT     'int'            @(1,1)
ID         'x'              @(1,5)  lid=0
ES         '='              @(1,7)
NUM        '42'             @(1,9)  val=42
PYC        ';'              @(1,11)
ID         'x'              @(2,1)  lid=0
MASIG      '+='             @(2,3)
NUM        '1'              @(2,6)  val=1
PYC        ';'              @(2,7)
KW_IF      'if'             @(3,1)
IPAREN     '('              @(3,4)
ID         'x'              @(3,5)  lid=0
MAOI       '>='             @(3,7)
NUM        '10'             @(3,10) val=10
LAND       '&&'             @(3,13)
ID         'x'              @(3,16) lid=0
DIS        '!='             @(3,18)
NUM        '13'             @(3,21) val=13
DPAREN     ')'              @(3,23)
ILLAVE     '{'              @(3,25)
ID         'x'              @(4,3)  lid=0
INC        '++'             @(4,4)
PYC        ';'              @(4,6)
DLLAVE     '}'              @(5,1)
EOF        ''               @(6,1)
```

## Autores

- **Joaquín Aguilar**
- **Rigoberto Aravena**
- **Benjamín Sánchez**
