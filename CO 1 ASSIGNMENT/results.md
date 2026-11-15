### Preprocessing (adjacency-list construction; graph seed = 2026+N)

| N | states V | edges E | build time (s) | farthest ward (hops) |
|---|---|---|---|---|
| 1,000 | 1,005 | 1,103 | 0.00 | 11 |
| 10,000 | 10,005 | 11,003 | 0.01 | 17 |
| 100,000 | 100,005 | 110,003 | 0.15 | 19 |
| 1,000,000 | 1,000,005 | 1,100,003 | 2.16 | 22 |

### Case: best (goal adjacent to pharmacy)

| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,000 | BFS | route | 2 | 1 | 1 | 1.0 | 7.0 | True | True | 0.0 |
| 1,000 | UCS | route | 28 | 10 | 20 | 1.0 | 7.0 | True | True | 0.0 |
| 1,000 | IDDFS | route | 3 | 3 | 8 | 1.0 | 7.0 | True | True | 0.0 |
| 10,000 | BFS | route | 2 | 1 | 1 | 1.0 | 4.0 | True | True | 0.0 |
| 10,000 | UCS | route | 14 | 5 | 10 | 1.0 | 4.0 | True | True | 0.0 |
| 10,000 | IDDFS | route | 3 | 3 | 6 | 1.0 | 4.0 | True | True | 0.0 |
| 100,000 | BFS | route | 2 | 1 | 1 | 1.0 | 9.0 | True | True | 0.0 |
| 100,000 | UCS | route | 502 | 152 | 361 | 1.0 | 9.0 | True | True | 0.2 |
| 100,000 | IDDFS | route | 3 | 3 | 19 | 1.0 | 9.0 | True | True | 0.0 |
| 1,000,000 | BFS | route | 2 | 1 | 1 | 1.0 | 9.0 | True | True | 0.0 |
| 1,000,000 | UCS | route | 290 | 75 | 217 | 1.0 | 9.0 | True | True | 0.1 |
| 1,000,000 | IDDFS | route | 3 | 3 | 13 | 1.0 | 9.0 | True | True | 0.0 |

### Case: average (5 random wards)

| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,000 | BFS | route | 398 | 227 | 171 | 5.6 | 34.8 | False | True | 0.1 |
| 1,000 | UCS | route | 806 | 644 | 214 | 6.4 | 33.8 | True | False | 0.7 |
| 1,000 | IDDFS | route | 850 | 850 | 44 | 5.6 | 34.8 | False | True | 0.5 |
| 10,000 | BFS | route | 6,117 | 4,911 | 1,562 | 9.4 | 51.6 | False | True | 2.2 |
| 10,000 | UCS | route | 7,944 | 6,118 | 2,040 | 10.2 | 42.4 | True | False | 6.7 |
| 10,000 | IDDFS | route | 44,976 | 44,976 | 89 | 9.4 | 51.6 | False | True | 22.3 |
| 100,000 | BFS | route | 66,928 | 54,088 | 17,336 | 10.4 | 56.6 | False | True | 66.3 |
| 100,000 | UCS | route | 79,969 | 64,203 | 19,955 | 11.4 | 47.4 | True | False | 202.4 |
| 100,000 | IDDFS | mixed | 449,703 | 449,703 | 130 | - | - | None | None | 521.5 |
| 1,000,000 | BFS | route | 381,227 | 231,210 | 150,022 | 10.6 | 53.8 | False | True | 545.9 |
| 1,000,000 | UCS | route | 672,440 | 511,427 | 178,517 | 10.8 | 53.6 | True | False | 3078.6 |
| 1,000,000 | IDDFS | mixed | 854,964 | 854,964 | 165 | - | - | None | None | 1316.0 |

### Case: worst-reachable (farthest ward)

| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,000 | BFS | route | 1,000 | 991 | 232 | 11.0 | 46.0 | True | True | 0.4 |
| 1,000 | UCS | route | 996 | 937 | 224 | 11.0 | 46.0 | True | True | 1.0 |
| 1,000 | IDDFS | route | 20,875 | 20,875 | 75 | 11.0 | 46.0 | True | True | 14.8 |
| 10,000 | BFS | route | 10,000 | 9,998 | 1,827 | 17.0 | 79.0 | False | True | 4.1 |
| 10,000 | UCS | route | 10,239 | 9,991 | 2,040 | 18.0 | 74.0 | True | False | 9.3 |
| 10,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 139 | - | - | None | None | 515.7 |
| 100,000 | BFS | route | 100,000 | 99,997 | 19,204 | 19.0 | 102.0 | False | True | 183.2 |
| 100,000 | UCS | route | 102,444 | 99,996 | 20,030 | 20.0 | 91.0 | True | False | 315.2 |
| 100,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 145 | - | - | None | None | 1179.2 |
| 1,000,000 | BFS | route | 1,000,000 | 999,994 | 186,580 | 22.0 | 115.0 | False | True | 2330.5 |
| 1,000,000 | UCS | route | 1,024,975 | 999,934 | 201,121 | 22.0 | 101.0 | True | True | 5576.1 |
| 1,000,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 170 | - | - | None | None | 1743.9 |

### Case: unreachable (isolated ward block)

| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,000 | BFS | no route | 1,000 | 1,000 | 232 | - | - | None | None | 0.5 |
| 1,000 | UCS | no route | 1,023 | 1,000 | 224 | - | - | None | None | 1.1 |
| 1,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 117 | - | - | None | None | 425.4 |
| 10,000 | BFS | no route | 10,000 | 10,000 | 1,827 | - | - | None | None | 6.0 |
| 10,000 | UCS | no route | 10,240 | 10,000 | 2,040 | - | - | None | None | 12.8 |
| 10,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 139 | - | - | None | None | 663.4 |
| 100,000 | BFS | no route | 100,000 | 100,000 | 19,204 | - | - | None | None | 189.3 |
| 100,000 | UCS | no route | 102,445 | 100,000 | 20,030 | - | - | None | None | 320.3 |
| 100,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 145 | - | - | None | None | 1094.3 |
| 1,000,000 | BFS | no route | 1,000,000 | 1,000,000 | 186,580 | - | - | None | None | 2276.0 |
| 1,000,000 | UCS | no route | 1,024,989 | 1,000,000 | 201,121 | - | - | None | None | 6413.6 |
| 1,000,000 | IDDFS | DNF(budget) | 1,000,001 | 1,000,000 | 170 | - | - | None | None | 1560.5 |

### Case: start==goal

| N | algo | result | generated | expanded | max frontier | depth | cost | cost-optimal | hop-optimal | time ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,000 | BFS | route | 1 | 0 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 1,000 | UCS | route | 1 | 1 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 1,000 | IDDFS | route | 1 | 1 | 0 | 0.0 | 0.0 | True | True | 0.0 |
| 10,000 | BFS | route | 1 | 0 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 10,000 | UCS | route | 1 | 1 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 10,000 | IDDFS | route | 1 | 1 | 0 | 0.0 | 0.0 | True | True | 0.0 |
| 100,000 | BFS | route | 1 | 0 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 100,000 | UCS | route | 1 | 1 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 100,000 | IDDFS | route | 1 | 1 | 0 | 0.0 | 0.0 | True | True | 0.0 |
| 1,000,000 | BFS | route | 1 | 0 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 1,000,000 | UCS | route | 1 | 1 | 1 | 0.0 | 0.0 | True | True | 0.0 |
| 1,000,000 | IDDFS | route | 1 | 1 | 0 | 0.0 | 0.0 | True | True | 0.0 |

### Empirical growth exponent alpha in metric ~ N^alpha (average case, 1k -> 1M)

| algo | alpha (generated) | alpha (max frontier) | alpha (time) |
|---|---|---|---|
| BFS | 0.99 | 0.98 | 1.21 |
| UCS | 0.97 | 0.97 | 1.21 |
| IDDFS | 1.72 | 0.31 | 1.63 |