# autonometrics

> ### *Sombras de la Autodeterminación*
>
> **Un instrumento para cuantificar la autodeterminación estructural a través de sistemas.**
>
> *Vemos sombras de autonomía, calibradas y reproducibles.*
> *Si la caverna detrás de ellas contiene un solo objeto o muchos,*
> *esta herramienta no lo decide.*

**Estado:** `alpha` — trabajo en curso, API inestable.

---

## Qué es

`autonometrics` es un instrumento en Python que toma una
trayectoria discreta — un autómata celular, una red booleana,
un log de agente, una simulación — y devuelve cuatro lecturas
normalizadas de cuán *autodeterminada* parece su estructura.
Cada lectura proviene de una tradición científica distinta;
juntas forman un pequeño **atlas de autonomía**: unas pocas
cartas que cubren el mismo territorio desde ángulos
operacionales diferentes.

Es una herramienta de medición, no una nueva teoría de la
autonomía. El paquete reúne medidas ya existentes, las
normaliza a una escala compartida `[0, 1]`, y permite comparar
puntos de sustratos muy distintos en el mismo espacio.

## Los cuatro ejes

| Eje | Pregunta que responde | Tradición | Referencia |
|---|---|---|---|
| **`closure`** | ¿Cuánta información del sistema se genera *desde dentro*? | Teoría de la información | Shannon (1948); Bertschinger et al. (2008); Albantakis (2021) |
| **`memory`** | ¿Cuánta predictibilidad del sistema la lleva *su propio pasado*? | Mecánica computacional | Crutchfield & Young (1989); Feldman & Crutchfield (2002) |
| **`constraint`** | ¿Cuán estrechamente se habilitan las restricciones del sistema *entre sí*? | Biología teórica | Montévil & Mossio (2015) |
| **`persistence`** | ¿Cuán bien resiste la estructura del sistema una perturbación pequeña? | Direccionalidad meta-operacional | Lee & McShea (2020) |

Las cuatro lecturas viven en `[0, 1]` y pueden ser graficadas,
correlacionadas y comparadas entre sustratos en el mismo espacio.

## Lo que el proyecto *no* afirma

Los cuatro ejes **no** se asumen como sombras de una única
cantidad subyacente. La fotografía empírica actual
(`v0.7.2a0`, benchmark sintético de 247 puntos) es honesta al
respecto: todas las correlaciones por pares quedan bajo
`|r| < 0.7`, el primer componente principal explica solo
`~47%` de la varianza, y los clusters en el atlas 4-D siguen
más a la *clase de sustrato* que a cualquier dimensión latente
de autonomía.

Por eso el paquete entrega un marco de medición, un benchmark,
los dropouts y una hipótesis de trabajo falsable — no una
teoría definitiva de la autonomía. La pregunta de nivel
(¿un objeto o varios?) queda como cuestión empírica abierta,
no como postulado.

El enunciado conceptual completo y los criterios de
falsación están en [`docs/PBA.es.md`](docs/PBA.es.md)
(español) y [`docs/PBA.md`](docs/PBA.md) (inglés). El
análisis pre-registrado de geometría del atlas en
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md);
notas de diseño por eje en
[`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md)
y [`docs/RAI.md`](docs/RAI.md).

## Instalación, uso y benchmarks

Para instalación, quickstart, ejemplos, benchmarks, roadmap y
demás detalles técnicos, ver el README en inglés:
[`README.md`](README.md).

Esta versión en español mantiene sincronizada la sección
introductoria; el resto de la documentación se irá traduciendo
progresivamente.
