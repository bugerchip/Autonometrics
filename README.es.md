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

Los cinco ejes **no** se asumen como sombras de una única
cantidad subyacente. La fotografía empírica actual
(`v0.8.0a0`, benchmark sintético de 645 puntos) es honesta al
respecto:

- Las correlaciones pareadas de los cuatro ejes de `v0.7.x`
  permanecen bajo `|r| < 0.7` en todos los sub-zoos donde
  están conjuntamente definidas, así que los cuatro ejes
  previos siguen cargando información distinta.
- El quinto eje (`coherence`) es empíricamente distinto de
  los primeros cuatro bajo adaptadores controlados: cuando
  el adaptador de referencia `PromisedCycle` se conduce con
  **dos fuentes independientes de variabilidad** en lugar de
  una, `r(closure, coherence)` cae de `+0.97` a `+0.48` y
  `r(coherence, p_env) ≈ 0` confirma la invariancia
  predicha de la fórmula al ruido del lado declarativo.
  Detalles y análisis pre-registrado en
  [`docs/CBA.md`](docs/CBA.md) y los snapshots diagnósticos
  bajo `docs/benchmarks/`.
- La nube completa de cinco ejes **no existe en el zoo
  actual**: cada clase de adaptador implementa o
  `get_causal_graph` (de modo que `constraint_closure`
  está definido) o `get_declared_executed` (de modo que
  `coherence` está definido), pero **nunca ambos**, dejando
  `n_valid_full = 0/645`. Por lo tanto, el atlas se lee
  mejor como un **mosaico / archipiélago** de subcartas de
  cuatro ejes superpuestas que como una nube única de cinco
  dimensiones. El veredicto está documentado en el
  follow-up de `v0.8.0a0` de
  [`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md).

Por eso el paquete entrega un marco de medición, un benchmark,
los dropouts y una hipótesis de trabajo falsable — no una
teoría definitiva de la autonomía. La pregunta de nivel
(¿un objeto o varios?) está **siendo empujada hacia Nivel 3
(mosaico) por el ciclo `v0.8.0a0` pero todavía sin decidir**;
la validación fuerte contra datos conductuales / tipo RAI se
difiere a `v0.9.0`, ciclo que también es el candidato natural
para un sustrato que finalmente cierre el hueco de cinco ejes.

El enunciado conceptual completo y los criterios de
falsación están en [`docs/PBA.es.md`](docs/PBA.es.md)
(español) y [`docs/PBA.md`](docs/PBA.md) (inglés). El
análisis pre-registrado de geometría del atlas en
[`docs/ATLAS_GEOMETRY.md`](docs/ATLAS_GEOMETRY.md); notas de
diseño por eje en
[`docs/CONSTRAINT_CLOSURE.md`](docs/CONSTRAINT_CLOSURE.md),
[`docs/RAI.md`](docs/RAI.md) y
[`docs/CBA.md`](docs/CBA.md). El log de releases en
[`CHANGELOG.md`](CHANGELOG.md).

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
