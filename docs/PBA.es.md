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
(`closure`, `memory`, `constraint_closure`, el eje RAI
planificado y el eje CBA planificado) sean la misma cantidad
escalar en notaciones distintas. Esa afirmación más fuerte, de
sostenerse, sería falsada por cualquier correlación por pares
notablemente menor a `|r| ≈ 1.0`. Empíricamente, los benchmarks
de `v0.5.0a0` y `v0.6.0a0` ya muestran correlaciones Pearson
por pares entre los tres ejes estructurales de `+0.32`, `-0.04`
y `-0.57`. Una lectura de Nivel 1 de PBA está, por tanto, ya
falsada, y nunca fue la lectura pretendida.

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
   cada uno de ellos.

Las dos razones restantes (los ejes motivacional y basado en
coherencia previstos para `v0.7.x`/`v0.8.x`) recibirán
diagnósticos análogos a medida que se incorporen: el dominio de
aplicabilidad de cada métrica debe quedar enunciado antes de que
esa métrica cuente como evidencia a favor o en contra de PBA.

## Estado actual de evidencia

A fecha de `v0.6.0a0`:

- Tres de las cinco razones están implementadas
  (`ratio_endo_total`, `memory_endo_ratio`,
  `constraint_closure`).
- Las pruebas internas de cordura muestran que las tres razones
  se comportan como la literatura predice en casos canónicos
  (series constantes, ruido i.i.d., ciclos deterministas,
  dinámicas mixtas regla-propia / impulsadas-por-entorno,
  restricciones aisladas frente a mutuamente sostenidas).
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
  todas por debajo del umbral `|r| < 0.7`. La bandera
  diagnóstica agregada (el peor de los tres pares) es `OK`. El
  tercer eje, entonces, transporta información que los dos
  primeros no codifican sobre el zoológico actual y rompe
  además la pared de saturación de clausura: los anillos ECA
  mantienen `constraint = 1.0`, mientras que los ciclos
  periódicos de un solo nodo y los autómatas autogenerados
  caen limpiamente a `constraint = 0.0`.

Por lo tanto, PBA está en la etapa de *hipótesis de trabajo
plausible con una limitación de grado diagnóstico explícitamente
mapeada y tres de los cinco ejes empíricamente distinguibles*,
no de *afirmación empírica*. Los documentos y demos del paquete
se redactan en consecuencia.

## Próximos puntos de decisión

- `v0.7.0a0` incorpora la cuarta razón — RAI-style de Deci &
  Ryan; primera oportunidad de comprobar si una razón tomada de
  una tradición distinta (psicología de la motivación)
  co-discrimina con las tres razones estructurales sobre un
  mismo sistema.
- `v0.8.0a0` añade el eje basado en coherencia (CBA);
  completar las cinco permite por primera vez evaluar la
  predicción anterior.
- Una pista de benchmarks dedicada (provisionalmente `v0.9.0a0`
  en el roadmap del README) es el lugar formal para la prueba
  de falsación, construida sobre las líneas base de `v0.5.x` y
  `v0.6.0a0`.

Si en cualquiera de estos puntos de control la predicción empieza
a fallar, este documento se actualiza con honestidad: el estatus
de PBA se rebaja y la comunicación del paquete sigue ese cambio.
