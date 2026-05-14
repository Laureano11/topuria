# Habit Tracker — Documentación de funcionalidades y flujos

---

## Visión general

Página web minimalista para el seguimiento de hábitos y objetivos personales. Permite registrar hábitos diarios, semanales, mensuales y anuales, visualizar el progreso por categoría, mantener rachas activas y gamificar el avance mediante un personaje con atributos.

---

## Estructura de la página

```
┌─────────────────────────────────────────┐
│         Banner — Frase del día          │
├─────────────────────────────────────────┤
│     Header — Título + Fecha + Personaje │
├─────────────────────────────────────────┤
│   Stats Row — Hoy / Semana / Mes / Año  │
├──────────────────────┬──────────────────┤
│                      │   Personaje      │
│  Hábitos diarios     ├──────────────────┤
│                      │  Progreso por    │
│  Rachas activas      │  categoría       │
│                      ├──────────────────┤
│  Hábitos semana /    │  Objetivos       │
│  mes / año (tabs)    │  anuales         │
└──────────────────────┴──────────────────┘
```

---

## Secciones y funcionalidades

### 1. Banner — Frase del día

- Se muestra en la parte superior de la página, siempre visible.
- Muestra una frase motivacional que rota diariamente.
- Incluye autor de la frase y fecha actual.
- Función: ambientar el inicio de la jornada con un estímulo positivo.

---

### 2. Header

- Muestra el nombre de la app, la fecha actual completa (día, número, mes, año).
- Incluye una vista rápida del personaje: nombre, nivel actual y XP acumulado.

---

### 3. Stats Row — Resumen de progreso

Cuatro métricas en fila, cada una con un anillo de progreso visual:

| Métrica | Descripción |
|---|---|
| **Hoy** | Hábitos diarios completados vs. total del día |
| **Esta semana** | Hábitos completados en la semana en curso |
| **Este mes** | Hábitos completados en el mes en curso |
| **Este año** | Hábitos completados en el año en curso |

Cada anillo refleja el porcentaje completado y se actualiza en tiempo real al hacer check en los hábitos.

---

### 4. Hábitos diarios

#### Descripción
Lista de hábitos que deben completarse **una vez por día**. El progreso se reinicia cada medianoche.

#### Atributos de cada hábito
- **Nombre** del hábito
- **Categoría**: Salud / Dinero / Estudio / Trabajo (con color distintivo)
- **Estado**: pendiente o completado

#### Flujo de uso
1. El usuario ve la lista de hábitos del día.
2. Hace clic en el checkbox de cada hábito al completarlo.
3. El hábito se tacha visualmente y reduce su opacidad.
4. El contador del día (ej. "3/7") se actualiza.
5. Al día siguiente, todos los checks se reinician.

#### Acciones disponibles
- ✓ Marcar hábito como completado
- Desmarcar hábito (si fue un error)
- Agregar nuevo hábito diario con el botón `+ nuevo hábito diario`

---

### 5. Rachas activas

#### Descripción
Objetivos de tipo contador de tiempo: miden cuánto tiempo lleva el usuario sin realizar (o realizando) una acción concreta.

#### Atributos de cada racha
- **Nombre** de la racha (ej. "Sin alcohol")
- **Tiempo activo**: días, horas y minutos desde el inicio
- **Barra de progreso**: avance visual hacia el objetivo definido
- **Récord personal**: mejor marca anterior
- **Objetivo**: duración meta definida por el usuario

#### Flujo de uso
1. El usuario crea una racha con nombre, fecha/hora de inicio y objetivo.
2. El contador corre en tiempo real (ej. "2d 13h 15m").
3. La barra de progreso avanza hacia el objetivo.
4. Si el usuario rompe la racha, puede reiniciarla desde cero.
5. Si supera su récord personal, el sistema lo registra.

#### Acciones disponibles
- Crear nueva racha con `+ nueva racha`
- Reiniciar racha (romper y volver a empezar)
- Editar objetivo de duración

---

### 6. Hábitos no diarios — Tabs: Semanal / Mensual / Anual

#### Descripción
A diferencia de los hábitos diarios, estos hábitos **no tienen ciclo fijo de reset diario**. El usuario hace check libremente cada vez que completa la acción.

#### Tabs disponibles
- **Semanal**: hábitos con frecuencia definida por semana (ej. "3 veces por semana")
- **Mensual**: hábitos con frecuencia definida por mes
- **Anual**: objetivos que se acumulan durante el año (ej. libros leídos)

#### Atributos de cada hábito no diario
- **Nombre** del hábito
- **Frecuencia objetivo** (ej. "3 veces por semana")
- **Conteo actual** vs. objetivo (ej. "2/3")
- **Indicadores visuales (puntos)**: uno por cada instancia completada y pendiente
- **Categoría**: Salud / Dinero / Estudio / Trabajo

#### Flujo de uso
1. El usuario accede al tab correspondiente (Semanal, Mensual o Anual).
2. Ve sus hábitos con el progreso actual.
3. Cada vez que completa la acción en cualquier momento, presiona el botón `✓ check`.
4. El conteo aumenta y se agrega un punto lleno en los indicadores visuales.
5. No hay reinicio automático por día — el usuario registra cuando quiere.

> **Ejemplo concreto**: "Libros leídos en el año" — el usuario puede hacer check cualquier día que termina un libro. El contador pasa de 7/24 a 8/24.

#### Acciones disponibles
- `✓ check` para registrar una nueva instancia completada
- Agregar nuevo hábito en cada frecuencia

---

### 7. Personaje

#### Descripción
Representación visual gamificada del progreso del usuario. Minimalista, sin elementos extravagantes.

#### Atributos
- **Nombre** del usuario
- **Nivel** (ej. Nivel 7)
- **XP acumulado** y XP necesario para el siguiente nivel
- **Barra de XP global**: progreso hacia el nivel siguiente
- **4 atributos** vinculados a las categorías de hábitos:
  - Salud
  - Dinero
  - Estudio
  - Trabajo

#### Flujo de progreso
1. Cada hábito completado suma XP al personaje (varía según categoría y tipo de hábito).
2. El XP acumulado llena la barra hacia el siguiente nivel.
3. Los atributos individuales (Salud, Dinero, etc.) suben cuando se completan hábitos de esa categoría.
4. Al acumular suficiente XP, el personaje sube de nivel.

#### Vinculación con hábitos
| Categoría hábito | Atributo del personaje |
|---|---|
| Salud | ❤️ Salud |
| Dinero | 💰 Dinero |
| Estudio | 📚 Estudio |
| Trabajo | 💼 Trabajo |

---

### 8. Progreso por categoría

Panel lateral que muestra, para el período seleccionado (mes por defecto), el porcentaje de hábitos completados agrupados por categoría:

- Salud
- Dinero
- Estudio
- Trabajo

Cada categoría tiene una barra de progreso con su color identificatorio y el porcentaje numérico.

---

### 9. Objetivos anuales

Subsección dentro de la columna derecha que destaca los objetivos de largo plazo del año. Funciona igual que los hábitos anuales: el usuario hace check libremente.

**Ejemplos de objetivos anuales:**
- Libros leídos (meta: 24)
- Cursos completados (meta: 6)
- Meses con inversión realizada (meta: 12)

---

## Categorías de hábitos

| Categoría | Color | Ejemplos |
|---|---|---|
| **Salud** | Verde | Gym, estirar, meditar, dormir 8h |
| **Dinero** | Marrón | Revisar finanzas, invertir, ahorrar |
| **Estudio** | Azul | Leer, tomar curso, aprender algo nuevo |
| **Trabajo** | Violeta | Proyecto personal, networking, reuniones |

---

## Tipos de hábito

| Tipo | Frecuencia | Reset | Forma de registrar |
|---|---|---|---|
| **Diario** | Cada día | Automático a medianoche | Checkbox diario |
| **Semanal** | N veces/semana | Manual o por período | Botón check libre |
| **Mensual** | N veces/mes | Manual o por período | Botón check libre |
| **Anual** | N veces/año | Manual o por período | Botón check libre |
| **Racha** | Tiempo continuo | Al romper la racha | Timer automático |

---

## Flujo completo de un día típico

```
1. El usuario abre la app a la mañana
       │
       ▼
2. Lee la frase motivacional del día
       │
       ▼
3. Revisa el resumen de progreso (Stats Row)
       │
       ▼
4. Va completando hábitos diarios durante el día
   → Gym ✓ → Estirar ✓ → Leer 50 páginas ✓
       │
       ▼
5. Verifica sus rachas activas
   → "Sin alcohol: 2d 13h 15min" ✓
       │
       ▼
6. Si completó un libro, va al tab Anual
   y hace check en "Libros leídos" → 8/24
       │
       ▼
7. Observa cómo suben los atributos del personaje
   y el XP acumulado hacia el nivel 8
       │
       ▼
8. Cierra la app hasta el día siguiente
```

---

## Notas de diseño

- La interfaz es **solo lectura en su estado actual** (maqueta HTML/CSS estática).
- Para producción, se requiere conectar a una base de datos o almacenamiento local (localStorage / backend).
- El timer de rachas necesita JavaScript con `setInterval` para actualización en tiempo real.
- Los checks diarios requieren persistencia por fecha para el reset automático.