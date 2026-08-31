# Mathematical skeleton of a generative-hierarchical system

## 1. Core idea

An ordinary dynamical system has a fixed state space:

\[
x_{t+1}=F(x_t),\qquad x_t\in X.
\]

For our model this is insufficient, because **the state space \(X\) itself must change**:

- new objects appear;
- new types of objects appear;
- new levels of description arise;
- new admissible interactions arise.

Therefore we take the fundamental state of the system to be the pair

\[
\boxed{\Omega_t=(\Theta_t,X_t)}
\]

where:

- \(X_t\) is **what currently exists**;
- \(\Theta_t\) is **which kinds of things can currently exist at all and which operations on them are meaningful**.

One may define

\[
\Theta_t=
(\mathcal T_t,\mathcal O_t,\mathcal R_t),
\]

where:

- \(\mathcal T_t\) is the set of types;
- \(\mathcal O_t\) are the observable quantities and states;
- \(\mathcal R_t\) are the admissible transformation rules.

Then the principal evolution operator is:

\[
\boxed{
U:(\Theta_t,X_t)\longrightarrow(\Theta_{t+1},X_{t+1})
}
\]

That is, **evolution is capable of changing its own ontology**.

More precisely still:

\[
U:
\bigsqcup_{\Theta}
\{\Theta\}\times X_\Theta
\longrightarrow
\bigsqcup_{\Theta}
\{\Theta\}\times X_\Theta.
\]

This is the central mathematical object of the construction.

---

## 2. Elementary entities

At time \(t\) there exist entities

\[
E_t=\{e_1,e_2,\dots,e_n\}.
\]

Each entity has a type

\[
\tau(e_i)\in\mathcal T_t
\]

and an internal state

\[
s(e_i)\in S_{\tau(e_i)}.
\]

The number of entities is not fixed:

\[
|E_{t+1}|\neq |E_t|
\]

is perfectly normal and permitted.

An entity may give rise to another:

\[
e_i\rightarrow(e_i,e_j),
\]

disappear:

\[
e_i\rightarrow\varnothing,
\]

or differentiate:

\[
\tau(e_i):A\rightarrow B.
\]

Thus the system is not a fixed container of objects, but a **generative set**.

---

## 3. Relations need not be stored as a graph

A classical graph requires fixing the relation in advance:

\[
(i,j)\in E.
\]

Instead of storing a ready-made list of edges, we introduce an **interaction function**:

\[
K(e_i,e_j,X_t)\in\mathbb R.
\]

It determines the extent to which two entities are able to interact **in the current state of the world**.

For example:

\[
K(i,j)=
\exp(-\|p_i-p_j\|).
\]

Then the local neighborhood of an entity is determined dynamically:

\[
N_i(X)=
\{j\mid K(i,j,X)>\alpha\}.
\]

Consequently,

\[
\boxed{\text{relations}=\text{function of current state}}
\]

rather than necessarily data recorded in advance.

The interaction network can rearrange itself completely without any change to any explicit list of edges.

---

## 4. The core primitive — the rule of becoming

Every rule has the form

\[
r:
(\text{local state},
\text{context})
\longrightarrow
\Delta X.
\]

For example:

\[
r(e_i)=
\begin{cases}
\operatorname{spawn}(B),& c(p_i)>0.8\\
\operatorname{differentiate}(C),&0.3<c(p_i)\le0.8\\
\operatorname{die},&c(p_i)\le0.3.
\end{cases}
\]

The state change may involve not only a change of numbers:

\[
\Delta X=
\{
\text{create},
\text{destroy},
\text{transform},
\text{move},
\text{emit},
\text{bind}
\}.
\]

The critically important point:

\[
\Delta\Theta
\]

is also admissible.

That is, a rule may create **new types of entities** and change the very set of admissible operations.

Such a rule is a metarule.

---

# 5. Mathematical definition of the emergence of a level

Let there be a group of microentities

\[
A=\{e_1,\dots,e_n\}.
\]

Introduce a coarse-graining map:

\[
\pi_A:X_A\rightarrow Y.
\]

It forgets most of the microdetail and extracts a macrovariable:

\[
y=\pi_A(x_1,\dots,x_n).
\]

For example, a vast number of microstates may be reduced to the parameters:

\[
y=
(\text{pressure},
\text{volume},
\text{contraction frequency}).
\]

But not every function should be regarded as a new level of description.

A criterion is needed.

## Axiom of emergent closure

If there exists a proper dynamics \(G\) such that

\[
\boxed{
\pi_A(U(x))
\approx
G(\pi_A(x))
}
\]

then the macrostate possesses an approximately **closed proper dynamics**.

In the ideal case:

\[
\pi_A\circ U=G\circ\pi_A.
\]

This can be represented by a commutative diagram:

\[
\begin{array}{ccc}
X_A & \xrightarrow{U} & X_A\\
\downarrow\pi &&\downarrow\pi\\
Y & \xrightarrow{G} & Y
\end{array}
\]

That is, one may either:

1. compute the microdynamics and then perform coarse-graining;
2. compute the dynamics of the macrostate directly.

If the results coincide or are sufficiently close, then \(Y\) is entitled to be regarded as an independent level of the model.

---

# 6. Birth of a new entity

If the condition

\[
d\big(
\pi U(x),
G\pi(x)
\big)<\varepsilon,
\]

holds, the system may create a macroobject

\[
m_A.
\]

Its realization:

\[
\rho(m_A)=A,
\]

and its state:

\[
s(m_A)=\pi_A(X_A).
\]

Then the fundamental transition:

\[
\boxed{
\{e_1,\dots,e_n\}
\Rightarrow
m_A
}
\]

The macroobject need not replace the microentities.

Both levels may exist simultaneously.

---

# 7. Recursive emergence of hierarchy

Macroentities can be processed by the same rules as microentities.

There were:

\[
e_1,e_2,\dots
\]

there arose:

\[
m_1,m_2,\dots
\]

then:

\[
\{m_1,m_2,m_3\}
\Rightarrow M.
\]

After that:

\[
\{M_1,M_2,\dots\}
\Rightarrow Z.
\]

We obtain a sequence of levels:

\[
L_0
\overset{\pi_0}{\longrightarrow}
L_1
\overset{\pi_1}{\longrightarrow}
L_2
\overset{\pi_2}{\longrightarrow}\cdots
\]

The number of levels need not be known in advance.

The system can discover them itself:

\[
\boxed{
L_{k+1}
=
\operatorname{Emergence}(L_k)
}
\]

---

# 8. Top-down feedback

Let a macroobject \(M\) have state

\[
y_M.
\]

It may constrain the behavior of the components:

\[
x_i(t+1)=
f_i(
x_i,
N_i,
y_M
).
\]

That is, a microentity depends not only on its immediate local neighborhood, but also on the state of the macrolevel.

This can be expressed through the set of admissible microstates:

\[
X_A\in C_M(y_M).
\]

The macrolevel imposes the constraint

\[
C_M:Y_M\rightarrow\mathcal P(X_A).
\]

We obtain a loop:

\[
\boxed{
\text{micro}
\xrightarrow{\pi}
\text{macro}
\xrightarrow{C}
\text{constraints on micro}
}
\]

The microlevel creates the macrolevel, and the macrolevel begins to constrain the microdynamics.

---

# 9. Minimal mathematical object

Working name: **Ontogenic System**.

\[
\boxed{
\mathfrak O=
(\Theta,X,R,\Pi,C)
}
\]

where:

- \(\Theta\) is the current ontology;
- \(X\) is the current realization of the world;
- \(R\) are the local generative rules;
- \(\Pi=\{\pi_i\}\) are the operators for detecting and compressing levels;
- \(C=\{C_i\}\) are the top-down constraints of the macrolevels.

The full dynamics:

\[
\boxed{
(\Theta_{t+1},X_{t+1})
=
U(
\Theta_t,
X_t,
R,
\Pi,
C,
\eta_t
)
}
\]

where \(\eta_t\) is the external environment, noise, or another external source of information.

---

# 10. Five basic axioms

## 1. Generativity

\[
|X_t|\text{ is not fixed.}
\]

Entities may arise and disappear.

## 2. Locality

\[
\Delta e_i=f(e_i,\operatorname{context}(e_i)).
\]

Global form arises from local interactions.

## 3. Ontological extensibility

\[
\Theta_{t+1}\neq\Theta_t
\]

is permitted.

The system may generate new types, operations, and forms of interaction.

## 4. Emergent closure

\[
\pi\circ U\approx G\circ\pi.
\]

A new level exists precisely when it possesses its own approximately closed dynamics.

## 5. Recursive universality

A macroentity is an admissible entity just like a microentity:

\[
m\in X.
\]

Therefore the process can repeat:

\[
\boxed{
\text{things}
\rightarrow
\text{systems of things}
\rightarrow
\text{systems of systems}
\rightarrow\cdots
}
\]

with no predetermined depth.

---

# 11. Algorithmic-information constraint

It is important not to turn the model into a claim about information arising from nothing.

For a deterministic system, roughly:

\[
K(X_t)
\lesssim
K(R)+K(X_0)+K(t).
\]

If the system receives information from the environment or from randomness:

\[
K(X_t)
\lesssim
K(R)+K(X_0)+K(\eta_{0:t}).
\]

That is, the construction does not create arbitrary algorithmic information out of nothing.

It does something else:

\[
\boxed{
\text{small description}
\Rightarrow
\text{huge unfolded structure}
}
\]

through recursive generation, dynamics, and use of the laws of the environment.

---

# 12. Minimal programming primitives

For a first implementation one may try to restrict oneself to six primitives:

```text
entity
rule
spawn
field
emerge
constraint
```

Their meaning:

### `entity`

Create or describe an existing entity.

### `rule`

Specify a local rule for changing state.

### `spawn`

Create a new entity or set of entities.

### `field`

Define a distributed context: a chemical field, potential, pressure, cost, signal, probability, and so on.

### `emerge`

Find a subsystem admitting a stable macrodescription:

\[
\pi\circ U\approx G\circ\pi
\]

and create a new entity from that macrodescription.

### `constraint`

Allow the macrolevel to constrain the space of admissible microstates:

\[
C_M:Y_M\rightarrow\mathcal P(X_A).
\]

---

# 13. Key principle

The most unusual primitive of this model is `emerge`.

It means not:

> create an object of such-and-such class;

but:

> find a subsystem that admits a closed macrodescription, and turn that description into a new entity.

Thus the central primitive becomes neither an object nor a relation, but:

\[
\boxed{
\text{local rule for the emergence of new structure}
}
\]

And the system as a whole becomes not merely a data structure, but a **structure of becoming**.
