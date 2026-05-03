# PBA como hipótesis falsable

> *Versión en español del documento canónico
> [`docs/PBA.md`](PBA.md). El inglés es la versión de referencia
> oficial; ante cualquier discrepancia, prevalece esa.*

> *Estado: borrador de trabajo. El argumento aquí planteado guía el
> diseño de `autonometrics` y es a su vez contrastable; este
> documento existe para que ese contraste pueda llevarse a cabo, y
> para que el paquete no pretenda que el principio ya está
> demostrado.*

## Qué afirma PBA

El **Principio de Bordes Autodeterminados** (PBA), en su forma de
trabajo actual, es una afirmación estructural sobre cómo los
sistemas determinan su propio comportamiento:

> La autodeterminación estructural de un sistema puede leerse como
> una *razón entre una magnitud interna y una magnitud total*,
> donde "magnitud" representa alguna cantidad (información,
> influencia causal, energía, restricción, etc.) a la que el
> comportamiento del sistema sea sensible.

En concreto, PBA predice que varias formalizaciones clásicas de la
autonomía y la autodeterminación
— Bertschinger / Albantakis (clausura informacional),
autopoiesis de Gershenson (autoproducción de componentes),
RAI de Deci & Ryan (regulación motivacional),
alineamiento basado en coherencia (CBA) y
cierre de restricciones de Montévil & Mossio —
son **cinco caras de una misma forma estructural**, no cinco
fenómenos no relacionados que casualmente se expresan como ratios.

Si PBA es correcto, las cinco métricas correspondientes, calculadas
sobre el mismo sistema, no deberían ser estadísticamente
independientes: deberían covariar de modos que la literatura de
cada formalismo predice.

## Qué tipo de unificación propone PBA

La frase "cinco caras de una misma forma estructural" está
elegida con intención y se presta a dos malas lecturas opuestas.
Cada una sería errónea de manera informativa. Esta sección fija
el punto medio.

### Tres niveles posibles de unificación

Distintas unificaciones científicas implican compromisos
ontológicos muy distintos. Conviene separarlas explícitamente.

**Nivel 1 — Identidad extensional.** "Estas N cantidades son
literalmente el mismo número expresado en notaciones distintas."
El caso canónico es la entropía: la entropía termodinámica, la
estadística de Boltzmann y la informacional de Shannon
resultaron ser una sola cantidad salvo conversión de unidades
(`S_termo = k_B · S_estad`, `H_Shannon = S_estad / ln 2`). Otros
ejemplos: `E = mc²`, la unificación de Maxwell entre
electricidad y magnetismo. Cuando una unificación así se
sostiene, **reduce la ontología**: N conceptos colapsan a uno y
el campo se reorganiza en torno a esa reducción. Estos casos son
raros y constituyen la unificación científica más fuerte
posible.

**Nivel 2 — Estructura compartida con coordenadas múltiples.**
"Estas N cantidades son vistas coordinadas de un mismo objeto
subyacente que *no es escalar*; ninguna de ellas captura el
objeto sola, pero juntas lo cubren, y están restringidas a
moverse de manera consistente como vistas del mismo objeto."
Ejemplos:

- **Color**. No es una sola cantidad. Es al menos
  tridimensional. RGB, HSV y CMYK son sistemas de coordenadas
  distintos sobre el mismo espacio perceptual, con reglas
  precisas para transformar uno en otro.
- **Big Five de personalidad**. Cinco dimensiones empíricamente
  estables (apertura, responsabilidad, extraversión,
  amabilidad, neuroticismo) recuperadas por análisis factorial
  sobre cuestionarios a través de culturas e idiomas. No
  reducibles a un solo eje; tampoco arbitrarias.
- **Temperatura antes de la teoría cinética (1700–1850)**.
  Múltiples definiciones operacionales (termómetro de
  mercurio, de gas, radiación de cuerpo negro) ordenaban
  sistemas de manera consistente por "más caliente que" sin
  que existiera todavía una teoría unificadora de qué cosa
  común estaban midiendo. La teoría cinética llegó casi un
  siglo después.
- **Espacio-tiempo en relatividad especial**. Espacio y tiempo,
  hasta entonces tratados como independientes, pasaron a ser
  coordenadas de un mismo objeto 4D cuya geometría de
  Minkowski impone relaciones específicas entre ellos.

Una unificación de Nivel 2 **no reduce la ontología**: la
**describe**. La afirmación es que existe un objeto en algún
sentido independiente del sistema de coordenadas, y que sus
múltiples definiciones operacionales son lo suficientemente
consistentes como para triangularlo.

**Nivel 3 — Agrupación arbitraria bajo una etiqueta común.**
"Estas N cantidades comparten nombre porque las pusimos en la
misma carpeta; no hay objeto subyacente." Muchas
"unificaciones" prematuras en trabajos teóricos terminan acá
cuando se las somete a contraste empírico. Un resultado de
Nivel 3 no es unificación; es un error taxonómico.

### PBA es Nivel 2, no Nivel 1

PBA **no** afirma que las cinco métricas que integra
(`closure`, `memory`, `constraint_closure`,
`rai_proxy_persistence` y el eje CBA planificado) sean la misma
cantidad escalar en notaciones distintas. Esa afirmación más
fuerte, de sostenerse, sería falsada por cualquier correlación
por pares notablemente menor a `|r| ≈ 1.0`. Empíricamente, los
benchmarks de `v0.5.0a0`, `v0.6.0a0` y `v0.7.0a0` ya muestran
correlaciones Pearson por pares entre los cuatro ejes
estructurales de `+0.32` (closure-memory), `-0.04`
(closure-constraint), `-0.57` (memory-constraint), `-0.44`
(closure-persistence), `-0.38` (memory-persistence) y `+0.05`
(constraint-persistence). Una lectura de Nivel 1 de PBA está,
por tanto, ya falsada — por seis pares de correlaciones que
quedan por debajo del `|r| ≈ 1.0` saturante — y nunca fue la
lectura pretendida.

Lo que PBA sí afirma es la lectura de Nivel 2:

> La autodeterminación estructural es un fenómeno real pero
> multidimensional. Cada uno de los cinco formalismos que
> incorpora el paquete operacionaliza una coordenada distinta
> de ese fenómeno. Las cinco coordenadas no son independientes
> — están restringidas por ser vistas del mismo objeto
> subyacente — pero tampoco son idénticas. La forma de su
> distribución conjunta sobre sistemas significativos es lo que
> PBA predice y lo que `autonometrics` mide.

La predicción que esto habilita es nítida: las correlaciones
por pares deberían ubicarse en una "zona dulce" — distintas de
cero (de lo contrario no hay objeto compartido) y por debajo
de la saturación (de lo contrario son redundantes), con signos
interpretables desde la teoría que generó cada formalismo. El
snapshot del benchmark descrito en "Estado actual de
evidencia" cae dentro de esa zona dulce para dos de los tres
pares actuales y ofrece una explicación de causa conocida para
el tercero (la clausura de Albantakis satura sobre el zoo
actual, lo que comprime cualquier relación lineal con ella
hacia cero por construcción).

### `autonometrics` como atlas de la autonomía

La descripción de una sola línea más precisa de lo que el
paquete propone es entonces:

> `autonometrics` es un *atlas* de la autonomía: un conjunto
> pequeño de cartas (métricas) que cubren el mismo territorio
> multidimensional desde ángulos operacionales distintos y se
> mantienen comparables entre sí gracias a una normalización
> compartida en `[0, 1]`.

Tres propiedades que esta lectura preserva y tres que abandona
merecen quedar enunciadas explícitamente.

**Preserva.**

- Falsabilidad. El atlas puede fallar (las correlaciones se
  vuelven aleatorias, los signos contradicen la teoría, las
  clases dejan de co-discriminar) y ese fallo es publicable.
- Comparabilidad cruzada entre tradiciones. Cinco métricas
  sobre el mismo plano son un instrumento real
  independientemente de que la afirmación unificadora se
  sostenga.
- Utilidad operacional. La medición tipo atlas ya se usa en
  campos donde el objeto subyacente es genuinamente
  multidimensional (color, personalidad, anatomía bajo
  homología); el precedente está maduro.

**Abandona.**

- La reducción dramática a una sola cantidad de Nivel 1. No
  estamos haciendo entropía.
- La promesa de que un número solo pueda representar la
  autonomía. No puede, y fingir lo contrario sería un error
  categorial.
- La expectativa de que las cinco métricas terminen
  coincidiendo en un único ranking de sistemas. No lo harán, y
  *no deberían* hacerlo si el objeto subyacente es realmente
  multidimensional.

Esta sección es el enunciado canónico del nivel en que opera
PBA. El resto del documento — criterios de falsación, teoremas
de dominio de aplicabilidad, estado de evidencia — debe leerse
bajo ella. Las referencias a "cinco caras de una misma forma
estructural" en otras partes del código y en el README son
abreviatura de la lectura de Nivel 2 que aquí se define.

## Por qué es una hipótesis y no una definición

La tentación es leer PBA como una *convención* — "elegimos llamar
autonomía a esta forma de ratio". Es una jugada coherente, pero no
es la jugada que se hace aquí. `autonometrics` trata PBA como una
**conjetura empírica sobre la estructura de una literatura
existente**, no como una definición estipulativa.

La diferencia importa porque:

- Una definición no puede estar equivocada; solo puede ser útil o
  inútil.
- Una conjetura sobre cómo se relacionan cinco tradiciones de
  investigación distintas *sí puede* estar equivocada, y por eso
  resulta informativa cuando sobrevive al contacto con datos.

`autonometrics` es el instrumento que expone la conjetura a ese
contacto.

## La predicción falsable

Una vez que el paquete tenga implementadas las cinco métricas con
forma de ratio (los hitos del roadmap son `v0.5.0a0` a `v0.7.0a0`),
la predicción toma una forma concreta:

> **Predicción.** En un conjunto de prueba curado de sistemas con
> grados conocidos de autodeterminación estructural
> (por ejemplo: ciclos de período `p`, redes booleanas acopladas a
> distintas intensidades de acoplamiento, agentes de aprendizaje
> por refuerzo con políticas de distinto grado de fundamento,
> respuestas Likert de estudios poblacionales sobre motivación
> autónoma vs heterónoma), las cinco razones PBA deberían:
>
> 1. Estar **correlacionadas de manera no trivial** entre sistemas
>    en los que la literatura subyacente predice un mismo gradiente
>    de autonomía.
> 2. **Co-discriminar** entre clases cualitativamente distintas que
>    la literatura predice que deberían diferir en autonomía
>    (por ejemplo: autómatas regidos por regla propia vs por ruido,
>    perfiles de motivación intrínseca vs extrínseca).
> 3. **Converger** en una misma región canónica del hipercubo
>    conjunto `[0, 1]^5` para una clase dada, en lugar de
>    dispersarse por él.

## Qué falsaría a PBA

La predicción es informativa porque puede fallar de formas
concretas y publicables:

- **Resultado de independencia.** Si en el conjunto de prueba las
  cinco razones resultan empíricamente independientes
  (correlaciones por pares centradas en cero, ningún componente
  principal compartido por encima del ruido), PBA colapsa a una
  *forma funcional común* sin un *constructo subyacente común*.
  El paquete seguiría siendo útil como tablero de cinco ejes, pero
  el argumento unificador estaría equivocado.

- **Resultado de anti-correlación.** Si las razones tiran
  sistemáticamente en direcciones opuestas en sistemas que la
  literatura considera paradigmáticamente autónomos, PBA estaría
  identificando mal lo que las cinco tradiciones miden; el
  argumento unificador no solo sería incorrecto, sino activamente
  engañoso.

- **Resultado de mezcla de clases.** Si la nube de puntos
  pentadimensional no separa mejor que el azar las clases
  autodeterminadas de las heterónomas, el principio carece de
  poder discriminativo y debería retirarse.

Cualquiera de estos resultados es un resultado científico válido.
PBA está diseñado para poder descartarse.

## Qué *no* falsaría a PBA

Para mantener honesto el contraste, hay que descartar
explícitamente dos coincidencias triviales:

- **Acuerdo trivial sobre casos degenerados.** Si las cinco razones
  devuelven el mismo número sobre una secuencia constante y sobre
  ruido i.i.d. uniforme, eso no es evidencia a favor de PBA; es
  evidencia de que cualquier normalizador razonable colapsa sobre
  entradas degeneradas. El conjunto de prueba debe incluir
  sistemas no degenerados, donde las razones se ven obligadas a
  discrepar si PBA está equivocado.

- **Correlación inducida por construcción.** Si las cinco métricas
  se implementan de modo que matemáticamente compartan la mayor
  parte de su varianza (por ejemplo: si todas terminan leyendo en
  última instancia la misma entropía condicional), la
  correlación aparente es un artefacto de implementación, no
  evidencia. Cada métrica debe implementarse desde su fuente
  primaria y auditarse en busca de solapamientos algebraicos
  ocultos.

## Por qué el proyecto sobrevive a una falsación de PBA

El valor operativo del paquete es **independiente del argumento
unificador**. Si PBA es falsado, `autonometrics` sigue siendo útil
como:

- una reimplementación multiplataforma y de pocas dependencias de
  cinco métricas de referencia que de otro modo están dispersas
  entre artículos, lenguajes y ecosistemas,
- un contenedor de datos `AutonomyProfile` estandarizado con
  metadatos de medición,
- un pequeño ecosistema de adaptadores para sustratos distintos
  (autómatas sintéticos, trayectorias CSV, futuros transcripts de
  LLM y encuestas),
- un plano canónico `[0, 1] × [0, 1]` para lecturas en dos ejes
  que no requiere que la afirmación sobre cinco ejes sea cierta.

Atar la supervivencia del proyecto a la verdad de PBA habría sido
una decisión de diseño frágil. Atarla a la corrección de las
métricas clásicas subyacentes — cada una publicada, citada y
defendida de manera independiente — es bastante más sólido.

## Dominio de aplicabilidad

PBA es una afirmación sobre *bordes autodeterminados*; las
métricas en las que se apoya tienen, por tanto, **regiones donde
son matemáticamente triviales**, no porque la métrica esté rota
sino porque en esas regiones el sistema mismo es degenerado desde
el punto de vista de la métrica. Reconocer explícitamente esas
regiones forma parte de la formulación honesta del principio.

La primera de esas regiones se identificó empíricamente en
`v0.5.0a0` y se caracterizó formalmente en `v0.5.1a0`:

> **Teorema de saturación de clausura (informal).** Para un sistema
> cuya dinámica es determinista y cuyo par observado `(S_t, E_t)`
> contiene todas las variables de las que depende la regla de
> transición, la clausura de Albantakis cumple `A = 1` por
> construcción.
>
> *Esquema de demostración.* Bajo esas condiciones
> `H(S_{t+1} | S_t, E_t) = 0`. Por la regla de la cadena,
> `H(S_{t+1} | E_t) = I(S_{t+1}; S_t | E_t) + H(S_{t+1} | S_t, E_t)`.
> El segundo término se anula, por lo que el numerador y el
> denominador del cociente de clausura son iguales.

El benchmark de `v0.5.0a0` hizo visible esta saturación: cada
autómata celular elemental, cada ciclo de período `p` y cada
`SimpleAutomaton` autogenerado del zoológico colapsó sobre la
recta vertical `closure = 1.0`. El enunciado teórico anterior
explica *por qué*. El diagnóstico que se incorpora en `v0.5.1a0`
(`examples/saturation_diagnostic.py`,
`docs/benchmarks/saturation_v0.5.1.csv`,
`docs/benchmarks/saturation_v0.5.1.png`) lo verifica empíricamente:
cuando se inyecta ruido tipo bit-flip en la trayectoria focal de un
ECA saturante con probabilidad `p`, la clausura cae de manera
monótona desde `1.000` en `p = 0` hasta `≈ 0.001` en `p = 0.5`,
con una caída ya visible en `p = 0.01` (clausura ≈ 0.81). La pared
es por tanto un **punto teórico frágil**, no un régimen robusto, y
cualquier valor de clausura por debajo de 1.0 informa sobre
observación parcial, dinámica estocástica o ruido de medición —
exactamente los tres modos de fallo que la métrica está diseñada
para detectar.

Tres consecuencias prácticas para PBA:

1. **Las métricas tienen regiones triviales, y está bien.**
   Leer `closure = 1.0` como "máxima autonomía" es incorrecto; se
   lee como "la métrica saturó porque el sistema es plenamente
   determinista y plenamente observado". Un mecanismo de relojería
   determinista cae en el mismo punto que un sistema con la mayor
   autoorganización posible.

2. **Dónde se corta "sistema" vs "entorno" mueve la métrica.**
   El cociente de Albantakis es relativo al par elegido `(S, E)`.
   Cambiar qué cuenta como sistema o qué cuenta como entorno puede
   desplazar la clausura entre 0 y 1 sin cambiar el proceso físico
   subyacente. El diseño del adaptador no es un acto neutro de
   conexión: es parte de la medición.

3. **PBA no puede prometer universalidad sobre regiones
   degeneradas.** El principio es informativo *fuera* de las
   regiones triviales de cada métrica. Cualquier afirmación sobre
   correlación empírica entre las cinco razones es, por tanto,
   una afirmación *condicionada* a evitar esas regiones en los
   sistemas del benchmark utilizado para la prueba.

### El cierre de restricciones complementa la pared, no la reemplaza

El tercer eje incorporado en `v0.6.0a0`,
`constraint_closure`, se añadió en parte para *sondear* la pared
de saturación identificada arriba. Su diseño (ver
[`docs/CONSTRAINT_CLOSURE.md`](CONSTRAINT_CLOSURE.md)) es
deliberadamente independiente de la teoría de la información: la
métrica lee solo la topología del grafo de dependencias causales
del sistema y cuenta la fracción de restricciones que están sobre
algún ciclo dirigido simple de longitud 2 o 3. Dos consecuencias
para la discusión sobre dominio de aplicabilidad:

1. **El cierre de restricciones no satura donde sí lo hace la
   clausura de Albantakis.** Un ciclo periódico determinista de
   un solo nodo da `closure = 1.0` y `constraint = 0.0`; un
   anillo ECA determinista da `closure = 1.0` y `constraint =
   1.0`. El tercer eje, entonces, *separa* sistemas que el
   primer eje se ve obligado a identificar, pero también tiene
   sus propias regiones de saturación: cualquier sistema con
   una sola restricción puntúa `0.0` y cualquier anillo
   periódico cuyas celdas se lean mutuamente puntúa `1.0`. PBA
   no escapa nunca de la necesidad de declarar un dominio de
   aplicabilidad por eje; sólo cambia qué eje es informativo
   sobre qué sistema.
2. **La independencia ahora se contrasta sobre un par
   adicional.** Con tres ejes existen tres correlaciones por
   pares (`closure-memory`, `closure-constraint`,
   `memory-constraint`); la salvaguarda contra correlación
   inducida por construcción de la sección anterior aplica a
   cada uno de ellos. El cuarto eje añadido en `v0.7.0a0` eleva
   el conteo a seis correlaciones por pares, y las seis se
   mantienen por debajo de `|r| < 0.7` en el zoológico v0.7.0a0
   (ver "Estado actual de evidencia" más abajo).

Las dos regiones de saturación del tercer eje son a su vez
teoremas formales, documentados y verificados en
[`docs/CONSTRAINT_CLOSURE.md` (sección Domain of applicability)](CONSTRAINT_CLOSURE.md#domain-of-applicability-added-in-v061a0):

- **Teorema A (cero trivial por restricción única).** Cualquier
  sistema con `n = 1` función de actualización devuelve
  `constraint = 0.0` por construcción (un ciclo simple de
  longitud 2 o 3 requiere al menos dos nodos distintos).
- **Teorema B (saturación por vecindad simétrica).** Cualquier
  grafo en el que cada nodo lee al menos un nodo que lo lee de
  vuelta devuelve `constraint = 1.0` por construcción (cada
  nodo está sobre un ciclo de longitud 2).

El diagnóstico de `v0.6.1a0`
(`docs/benchmarks/constraint_density_v0.6.1.{csv,png,log.txt}`)
verifica ambos en conjunto barriendo la densidad de conexión
sobre un zoológico Kauffman y observando que la curva camina
monotonamente desde `constraint ≈ 0.14` en `K = 1` (frontera
inferior, dispersa) hasta `constraint = 1.00 ± 0.00` para
`K ≥ 6` con `n = 10` (frontera superior, densa). Los adapters
de un solo nodo y los anillos periódicos densos quedan
correctamente identificados como **fuera del dominio
discriminativo de la métrica**, no como sistemas de baja o alta
autonomía.

### La persistencia satura en ambos extremos del coupling focal

El cuarto eje incorporado en `v0.7.0a0`,
`rai_proxy_persistence`, se añadió en parte para someter la
afirmación del atlas a una *prueba transversal a tradiciones*:
clausura / memoria / restricciones son teóricos de la
información y de grafos; persistencia es un proxy estructural
**dinámico** tomado de la literatura sobre direccionalidad a
metas (Lee & McShea 2020) y adaptado a sistemas sin meta
externa explícita. Su diseño está documentado en
[`docs/RAI.md`](RAI.md). Como los tres ejes anteriores, la
persistencia tiene regiones de saturación propias que deben
enunciarse explícitamente:

1. **La persistencia satura distinto en distintas fronteras.**
   Sobre un `KauffmanNetwork` barrido a través del coupling
   focal, el diagnóstico de `v0.7.0a0`
   (`docs/benchmarks/persistence_v0.7.0.{csv,png,log.txt}`)
   observa una **forma de U**: la métrica se sienta cerca de
   `1.0` en ambos extremos del eje de coupling (extremo
   izquierdo: la trayectoria focal colapsa a un punto fijo y
   cualquier perturbación queda absorbida trivialmente;
   extremo derecho: el bit-flip nunca entra en la regla que
   computa el focal en `t_star + 1`, así que la perturbación
   es invisible por construcción), y dipa en el medio, donde
   sí se observa propagación real de la perturbación. El rango
   útil no trivial de la métrica sobre redes booleanas vive
   en los couplings intermedios; ambas colas son regiones de
   absorción trivial de naturaleza distinta.
2. **La independencia ahora se contrasta sobre seis pares.**
   Con cuatro ejes existen seis correlaciones por pares; la
   salvaguarda contra correlación inducida por construcción
   aplica a cada una. En el benchmark v0.7.0a0 las seis pasan
   el filtro `|r| < 0.7`.

Los dos regímenes de saturación de la persistencia se
registran como hallazgos provisionales en este release.
Formalizarlos como teoremas con nombre (análogos a Teorema A /
Teorema B para `constraint_closure`) es el contenido planeado
del ciclo de mantenimiento `v0.7.1`, conjuntamente con el
barrido de magnitud de perturbación ya diferido allí en
`docs/RAI.md`.

La razón restante (el eje basado en coherencia previsto para
`v0.8.x`) recibirá un diagnóstico análogo a medida que se
incorpore: el dominio de aplicabilidad de cada métrica debe
quedar enunciado antes de que esa métrica cuente como evidencia
a favor o en contra de PBA.

### Geometría del atlas: ¿son los cuatro ejes proyecciones de un único objeto?

El benchmark de cuatro ejes pasa el filtro de falsación
`|r| < 0.7` por pares en cada release. Ese resultado descarta la
lectura **Nivel 1** fuerte de PBA (un único escalar en
notaciones distintas), pero **no** decide entre **Nivel 2** (un
objeto multidimensional, cuatro proyecciones) y **Nivel 3**
(varios objetos compartiendo etiqueta). Ambas lecturas son
consistentes con la misma tabla de correlaciones.

El ciclo `v0.7.2a0` somete la lectura Nivel 2 a una *prueba
estructural parcial* analizando la geometría de la nube 4-D que
produce el benchmark extendido. La pre-registración está en
[`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md); el analizador es
`examples/atlas_geometry.py`; los snapshots están en
`docs/benchmarks/atlas_geometry_v0.7.2a0.{json,log.txt,png}`.

Los indicadores pre-registrados se anclan en convenciones de
manual (Jolliffe 2002 para fracciones de varianza PCA, Rousseeuw
1987 para rangos de silueta) y quedaron fijados antes de
ejecutar el análisis extendido. Sobre el zoológico extendido
(`n_valid = 247` de `405`):

| Indicador          |   Valor | Banda pre-registrada                                |
|--------------------|--------:|-----------------------------------------------------|
| `λ_1`              | `0.469` | `[0.40, 0.70)` — PCA inconcluso                     |
| `λ_1 + λ_2`        | `0.809` | `[0.65, 0.85)` — baja-dimensionalidad parcial       |
| `s(k* = 5)`        | `0.642` | `≥ 0.50` — estructura fuerte de clusters            |
| Alineación cluster |       — | 4 de 5 clusters dominados por una clase de adapter |

La combinación no encaja limpiamente en ninguno de los tres
resultados pre-registrados. PCA cae en la banda *inconclusa* de
Outcome B; la silueta cae en la banda *cluster fuerte* de
Outcome A; los clusters **no** son cross-adapter, así que la
ruta de Outcome A queda bloqueada. El veredicto honesto, escrito
en [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md), es

> **Inconcluso sobre la cuestión de nivel (lectura PCA), con un
> *overlay* sugestivo de Nivel 3 (lectura de clustering).**

Tres consecuencias concretas para el marco:

1. **Nivel 2 deja de estar "respaldado por geometría
   estructural".** La nube 4-D no es efectivamente 1-D ni
   efectivamente 2-D. Carga estructura no trivial sobre al menos
   tres de sus cuatro componentes PCA.
2. **Nivel 3 tampoco puede declararse con esta evidencia.** Los
   umbrales de isotropía (`λ_1 < 0.40`,
   `λ_1 + λ_2 < 0.65`) no se cruzan, aunque la geometría de
   clusters sí siga al sustrato.
3. **La cuestión de nivel se empuja a v0.9.0.** La validación
   conductual contra RAI sobre transcripts es ahora la única
   ruta que puede arbitrar Nivel 2 vs Nivel 3 limpiamente. La
   geometría estructural por sí sola, sobre el zoológico actual,
   está genuinamente sub-determinada.

Se levanta también una **bandera de paradoja de Simpson**: varias
de las seis correlaciones globales por pares difieren de sus
contrapartes intra-cluster o intra-adapter por más de `0.30`. El
caso más extremo es `closure–persistence`: global `−0.61`,
dentro de `KauffmanNetwork` `−0.07`, dentro de `SimpleAutomaton`
`−1.00`. El resultado de falsación (`|r_global| < 0.7` en cada
par) sobrevive sobre la muestra extendida, pero las magnitudes
de las correlaciones globales son en parte artefactos de la
mezcla de sustratos en el zoológico.

El veredicto está condicionado por la cláusula de
`no-degeneración`: el barrido extendido produce *dropouts* en el
39 % de las configuraciones, concentrados sobre `ECASystem` y
`KauffmanNetwork` (51 — 55 % de tasa interna por adapter) y cero
sobre `PeriodicCycle` y `SimpleAutomaton`. Esto es en sí mismo
un hallazgo estructural — el conjunto de métricas tiene un punto
ciego conjunto selectivo para los adapters celulares y de redes
— y queda documentado como tal en
[`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md).

## Estado actual de evidencia

A fecha de `v0.7.2a0`:

- Cuatro de las cinco razones están implementadas
  (`ratio_endo_total`, `memory_endo_ratio`,
  `constraint_closure`, `rai_proxy_persistence`).
- Las pruebas internas de cordura muestran que las cuatro
  razones se comportan como la literatura predice en casos
  canónicos (series constantes, ruido i.i.d., ciclos
  deterministas, dinámicas mixtas regla-propia /
  impulsadas-por-entorno, restricciones aisladas frente a
  mutuamente sostenidas, propagación de perturbación bajo
  determinismo, absorción de perturbación bajo colapso a punto
  fijo, invisibilidad de perturbación bajo coupling externo
  total).
- Se ejecutó un primer mini-benchmark con dos ejes en
  `v0.5.0a0` (snapshot bajo
  `docs/benchmarks/v0.5.0a0.{csv,png,log.txt}`). Sobre 48
  puntos válidos de 69 configuraciones,
  `Pearson r(closure, memory) = +0.32` y
  `Spearman r(closure, memory) = +0.56`, ambos por debajo del
  umbral `|r| < 0.7` que este documento usa como señal de
  falsación.
- El diagnóstico de saturación de `v0.5.1a0` confirma que la
  pared vertical en `closure = 1.0` observada en ese benchmark
  es el teorema de saturación de clausura anterior, no un fallo
  de la métrica: inyectar ruido bit-flip pulla la clausura
  fuera de la pared de forma monótona.
- El benchmark de `v0.6.0a0` añade el tercer eje al mismo
  zoológico (snapshot bajo
  `docs/benchmarks/v0.6.0a0.{csv,png,log.txt}`): sobre 48
  puntos válidos de 69 configuraciones, las tres correlaciones
  Pearson son
  `r(closure, memory) = +0.32`,
  `r(closure, constraint) = -0.04`,
  `r(memory, constraint) = -0.57`,
  todas por debajo del umbral `|r| < 0.7`.
- El benchmark de `v0.7.0a0` añade el cuarto eje al mismo
  zoológico (snapshot bajo
  `docs/benchmarks/v0.7.0a0.{csv,png,log.txt}`): sobre 48
  puntos válidos de 69 configuraciones, las seis correlaciones
  Pearson son
  `r(closure, memory) = +0.32`,
  `r(closure, constraint) = -0.04`,
  `r(closure, persistence) = -0.44`,
  `r(memory, constraint) = -0.57`,
  `r(memory, persistence) = -0.38`,
  `r(constraint, persistence) = +0.05`,
  todas por debajo del umbral `|r| < 0.7`. La bandera
  diagnóstica agregada (el peor de los seis pares) es `OK`.
- El benchmark extendido de `v0.7.2a0` escala `n_seeds` de 5 a
  30 sobre el mismo zoológico (snapshot bajo
  `docs/benchmarks/v0.7.2a0.{csv,png,log.txt}`). Sobre `247`
  puntos válidos (de `405` configuraciones, con el patrón de
  *dropouts* documentado en
  [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md)) las seis
  correlaciones Pearson son
  `r(closure, memory) = +0.27`,
  `r(closure, constraint) = +0.04`,
  `r(closure, persistence) = -0.61`,
  `r(memory, constraint) = -0.52`,
  `r(memory, persistence) = -0.33`,
  `r(constraint, persistence) = -0.07`,
  todas de nuevo por debajo del umbral `|r| < 0.7`. El cuarto
  eje sigue transportando información que los tres primeros no
  codifican, también sobre el zoológico extendido. La prueba
  transversal a tradiciones de la hipótesis del atlas es parcial
  en este punto: el proxy estructural pasa el control
  estructural, pero la validación fuerte contra RAI conductual /
  transcripción se difiere a `v0.9.0`.
- El análisis de geometría del atlas de `v0.7.2a0` (PCA +
  k-means + silueta + correlaciones condicionales sobre el
  mismo zoológico extendido) deja la cuestión de nivel en un
  estado honestamente *inconcluso* con un *overlay sugestivo de
  Nivel 3*; detalles y umbrales pre-registrados en
  [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md) y resumen en la
  subsección *Geometría del atlas* arriba.

Por lo tanto, PBA está en la etapa de *hipótesis de trabajo
plausible con limitaciones de grado diagnóstico mapeadas en tres
de los cuatro ejes (saturación bajo determinismo, cero trivial
por restricción única, saturación por vecindad simétrica; las
fronteras de la persistencia se registran como hallazgos
provisionales a formalizar en v0.7.1), cuatro de los cinco ejes
empíricamente distinguibles sobre el zoológico actual y la
cuestión Nivel 2 vs Nivel 3 genuinamente sub-determinada sobre
el dominio estructural a la espera de la validación conductual
de v0.9.0*, no de *afirmación empírica*. Los documentos y demos
del paquete se redactan en consecuencia.

## Próximos puntos de decisión

- `v0.7.1a0` formaliza los dos regímenes de frontera de la
  persistencia (colapso de coupling bajo e invisibilidad de
  coupling alto) como teoremas con nombre análogos a Teorema A
  / Teorema B para `constraint_closure`, e incorpora el
  barrido de magnitud de perturbación diferido desde
  `v0.7.0a0` en `docs/RAI.md`.
- `v0.7.2a0` (este release) ejecuta el análisis de geometría
  del atlas pre-registrado en
  [`docs/ATLAS_GEOMETRY.md`](ATLAS_GEOMETRY.md). Veredicto
  arriba.
- `v0.8.0a0` añade el eje basado en coherencia (CBA);
  completar las cinco permite por primera vez evaluar la
  predicción anterior.
- `v0.9.0a0` añade el adapter de transcript LLM y la pasada de
  validación fuerte contra datos conductuales / RAI-style, el
  hogar formal de la prueba de falsación, construida sobre las
  líneas base de `v0.5.x`, `v0.6.x` y `v0.7.x`. **La cuestión
  Nivel 2 vs Nivel 3, actualmente sub-determinada sobre el
  dominio estructural, se decide aquí o queda abierta.**

Si en cualquiera de estos puntos de control la predicción empieza
a fallar, este documento se actualiza con honestidad: el estatus
de PBA se rebaja y la comunicación del paquete sigue ese cambio.
