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
dinámica generalmente restringida de Farnsworth (GCD) —
son **cinco caras de una misma forma estructural**, no cinco
fenómenos no relacionados que casualmente se expresan como ratios.

Si PBA es correcto, las cinco métricas correspondientes, calculadas
sobre el mismo sistema, no deberían ser estadísticamente
independientes: deberían covariar de modos que la literatura de
cada formalismo predice.

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

## Estado actual de evidencia

A fecha de `v0.4.0a0`:

- Dos de las cinco razones están implementadas
  (`ratio_endo_total`, `memory_endo_ratio`).
- Las pruebas internas de cordura muestran que ambas razones se
  comportan como la literatura predice en casos canónicos
  (series constantes, ruido i.i.d., ciclos deterministas,
  dinámicas mixtas regla-propia / impulsadas-por-entorno).
- Aún no se ha corrido ninguna validación entre sistemas contra un
  conjunto de prueba curado de manera independiente.

Por lo tanto, PBA está en la etapa de *hipótesis de trabajo
plausible*, no de *afirmación empírica*. Los documentos y demos
del paquete se redactan en consecuencia.

## Próximos puntos de decisión

- `v0.5.0a0` añade RAI; primera oportunidad de comprobar si una
  razón tomada de una tradición distinta (psicología de la
  motivación) co-discrimina con las dos razones informacionales
  sobre un mismo sistema.
- `v0.6.0a0` y `v0.7.0a0` añaden CBA y GCD respectivamente;
  completar las cinco permite por primera vez evaluar la
  predicción anterior.
- Una pista de benchmarks dedicada (provisionalmente `v0.9.0a0`
  en el roadmap del README) es el lugar formal para la prueba de
  falsación.

Si en cualquiera de estos puntos de control la predicción empieza
a fallar, este documento se actualiza con honestidad: el estatus
de PBA se rebaja y la comunicación del paquete sigue ese cambio.
