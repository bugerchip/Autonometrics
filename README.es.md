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
un log de agente, una simulación, y desde `v0.8.0a0` también
un sistema que publica su trayectoria *declarada* junto a la
*ejecutada* — y devuelve hasta **cinco lecturas normalizadas**
de cuán *autodeterminada* parece su estructura. Cada lectura
proviene de una tradición científica distinta; juntas forman
un pequeño **atlas de autonomía**: unas pocas cartas que cubren
el mismo territorio desde ángulos operacionales diferentes.

Es una herramienta de medición, no una nueva teoría de la
autonomía. El paquete reúne medidas ya existentes, las
normaliza a una escala compartida `[0, 1]`, y permite comparar
puntos de sustratos muy distintos en el mismo espacio.

## Los cinco ejes

| Eje | Pregunta que responde | Tradición | Referencia |
|---|---|---|---|
| **`closure`** | ¿Cuánta información del sistema se genera *desde dentro*? | Teoría de la información | Shannon (1948); Bertschinger et al. (2008); Albantakis (2021) |
| **`memory`** | ¿Cuánta predictibilidad del sistema la lleva *su propio pasado*? | Mecánica computacional | Crutchfield & Young (1989); Feldman & Crutchfield (2002) |
| **`constraint`** | ¿Cuán estrechamente se habilitan las restricciones del sistema *entre sí*? | Biología teórica | Montévil & Mossio (2015) |
| **`persistence`** | ¿Cuán bien resiste la estructura del sistema una perturbación pequeña? | Direccionalidad meta-operacional | Lee & McShea (2020) |
| **`coherence`** | ¿Cuán bien sigue la trayectoria *ejecutada* del sistema a la *declarada*? | Akrasia → disonancia cognitiva → alineamiento de IA | Festinger (1957); Sheeran (2002); Lanham (2023); Turpin (2023) |

Las cinco lecturas viven en `[0, 1]` y pueden ser graficadas,
correlacionadas y comparadas entre sustratos que expongan la
capacidad relevante. Las primeras cuatro requieren solo una
trayectoria de estado / entorno; la quinta además requiere un
par paralelo `(declarado, ejecutado)`, que solo los adaptadores
con una capa declarativa explícita exponen. Los adaptadores
que no implementan esa capa reportan `coherence = None` de
forma honesta, en línea con la misma política de dropout que
ya se usa para `constraint_closure` (solo grafo) y
`persistence` (solo replay).

## Lo que el proyecto *no* afirma

La hipótesis más fuerte posible — que las cinco medidas de
autonomía son la misma cantidad en distintas notaciones, al
estilo `H_Shannon = S_stat / ln 2` — quedó **falsada por el
segundo benchmark**. Las correlaciones pareadas observadas en
`v0.5.x` — `v0.7.x` se sientan en `+0.32` (closure-memory),
`-0.04` (closure-constraint), `-0.57` (memory-constraint),
`-0.44` (closure-persistence), `-0.38` (memory-persistence) y
`+0.05` (constraint-persistence): seis pares por debajo de la
saturación, seis piezas de evidencia de que no estamos mirando
una sola cantidad. Es la lectura de **Nivel 1** (Level 1) y ya
cayó.

La hipótesis intermedia — que existe **un objeto
multidimensional** y que cada eje es una coordenada distinta
del mismo, al modo en que RGB y HSV son vistas del mismo
espacio de color, o el Big Five recupera coordenadas de la
personalidad por análisis factorial — sí es lo que el paquete
implementa y prueba. La predicción es nítida: las correlaciones
deberían sentarse en un punto óptimo, distintas de cero
(comparten objeto) y bajo saturación (no son redundantes). Esa
es la lectura de **Nivel 2** (Level 2) que el pre-registro de
geometría del atlas en `v0.7.2a0` puso a prueba.

El ciclo `v0.8.0a0` empujó el veredicto hacia abajo. El quinto
eje (`coherence`, CBA / U de Theil) se sumó esperando
triangular el mismo objeto desde un sexto ángulo; en cambio,
los datos mostraron tres cosas. Las cuatro correlaciones
previas siguen bajo `|r| < 0.7` (los ejes aún cargan
información distinta). El quinto eje es empíricamente
independiente bajo control causal: `r(closure, coherence)` cae
de `+0.97` a `+0.48` cuando `PromisedCycle` se alimenta con
**dos fuentes independientes de variabilidad** en lugar de
una, y `r(coherence, p_env) ≈ 0` confirma la invariancia
predicha por la fórmula respecto al ruido del canal
declarativo. Y la nube completa cinco-dimensional **no existe
sobre el zoológico actual**: `n_valid_full = 0/645`, porque
ningún adapter expone simultáneamente `get_causal_graph` y
`get_declared_executed`.

El atlas se lee entonces mejor como un **mosaico / archipiélago**
(mosaic / archipelago) de sub-cartas de cuatro ejes superpuestas
que como una nube unificada cinco-dimensional. La pregunta de
fondo — un objeto multidimensional o varios — está empujada
hacia **Nivel 3** (Level 3) por este ciclo, pero **aún no
decidida**: la geometría estructural sola no puede arbitrarlo.
Solo la validación contra datos conductuales, externa al
repositorio, puede hacerlo, y queda diferida a estudios
construidos sobre el adapter LLM (LLM adapter) entregado en
`v0.9.0a0`.

Así el paquete entrega un **marco de medición, un benchmark,
los dropouts, y una hipótesis de trabajo falsable** — no una
teoría definitiva de la autonomía. El planteamiento conceptual
completo y los criterios de falsación viven en
[`docs/PBA.md`](docs/PBA.md) (inglés) y
[`docs/PBA.es.md`](docs/PBA.es.md) (español); las notas de
diseño por eje, en
[`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md),
[`docs/RAI.md`](docs/RAI.md) y
[`docs/CBA.md`](docs/CBA.md); el log de releases, en
[`CHANGELOG.md`](CHANGELOG.md).

## ¿Navaja suiza o ensalada? — Auto-evaluación

Un crítico razonable podría preguntar: ¿son estos cinco ejes
un instrumento coherente o una colección de métricas inconexas
con un mismo logo? Esta sección responde honestamente.

### Por qué creemos que es un instrumento coherente

- Forma matemática unificada: cada eje vive en `[0, 1]` con la
  misma firma "interno / total".
- Protocolo único (`AutonomySystem`); cualquier sustrato entra
  por una sola puerta.
- Umbrales de falsación pre-registrados para cada eje; el
  proyecto se compromete a poder fallar.
- Cada eje está anclado en una tradición de investigación
  publicada con al menos una referencia explícita: `closure` de
  Albantakis & Bertschinger (con el linaje IIT de Tononi);
  `memory` del programa de entropía en exceso (excess entropy)
  de Crutchfield; `constraint` de Montévil & Mossio;
  `persistence` de Lee & McShea (con Deci & Ryan / SDT como la
  referencia conductual diferida); `coherence` de la tradición
  de disonancia cognitiva (cognitive dissonance) de Festinger
  (con la literatura de fidelidad de Chain-of-Thought en AI
  alignment como aplicación contemporánea). Ninguno se inventa
  desde cero.

### Dónde la crítica tiene mérito

- Las cinco tradiciones detrás de los ejes pertenecen a campos
  genuinamente distintos. Combinarlas es una apuesta
  metodológica, no un hecho establecido.
- El veredicto de la geometría del atlas en `v0.8.0a0` fue
  "mosaico, no variedad" (mosaic, not manifold;
  `n_valid_full = 0/645`). Los cinco ejes no abarcan
  conjuntamente una nube 5D limpia en el zoológico actual.
- `rai_proxy_persistence` es un proxy estructural cuya
  validación fuerte contra RAI conductual queda diferida a
  estudios externos. Hasta que eso ocurra, la etiqueta "RAI"
  es provisional.
- Vocabulario como "PBA", "atlas mosaico" (mosaic atlas) o
  "agujero de cinco ejes" (five-axis hole) es interno a este
  proyecto y requiere leer la documentación para tener
  sentido.
- Aún no contamos con un paper revisado por pares que
  describa el paquete como un todo.

### Qué implica esto para el usuario potencial

Si trabajas en:
- IIT / consciencia / autonomía estructural → los ejes que
  reconocerás (`closure`, `constraint_closure`) están bien
  implementados y bien fundamentados.
- AI alignment / agentes LLM → `coherence` (CBA / U de Theil
  sobre trayectorias declaradas vs ejecutadas) mapea
  directamente sobre las preguntas de fidelidad de
  Chain-of-Thought.
- Investigación SDT motivacional pura → trata
  `rai_proxy_persistence` como un candidato estructural
  pendiente de validación; no lo equipares aún con C-RAI.
- Síntesis cross-tradicional → esta es exactamente la apuesta
  que hace el paquete; encontrarás los ingredientes
  pre-ensamblados.

Si nada de lo anterior encaja con tu trabajo, este paquete
probablemente no es tu herramienta — y preferimos que lo
sepas en 90 segundos antes que después de instalarlo.

## Instalación

### Desde PyPI (recomendado)

```bash
pip install --pre autonometrics
```

Para las dependencias opcionales de gráficos / benchmarks:

```bash
pip install --pre "autonometrics[viz]"
```

> El flag `--pre` es necesario mientras el paquete está en
> `alpha`. Cuando se publique una versión no-alpha, bastará
> con `pip install autonometrics`.

### Desde código fuente (modo desarrollo)

```bash
git clone https://github.com/bugerchip/Autonometrics.git
cd Autonometrics
pip install -e ".[dev,viz]"
```

Requiere Python 3.10 o superior. El paquete base solo depende
de `numpy`. El extra `viz` agrega `matplotlib`, usado por los
scripts de plotting del benchmark.

## Uso, ejemplos y benchmarks

Para quickstart, ejemplos, benchmarks, roadmap y demás detalles
técnicos, ver el README en inglés: [`README.md`](README.md).

Esta versión en español mantiene sincronizada la sección
introductoria y la de instalación; el resto de la documentación
se irá traduciendo progresivamente.
