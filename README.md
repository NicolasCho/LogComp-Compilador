# Status dos testes

![git status](http://3.129.230.99/svg/NicolasCho/LogComp-Compilador/)


## Diagrama sintático

![Diagrama sintático](imgs/ds_roteiro3.png "DS")

## EBNF

    EXPRESSION = TERM, { ("+" | "-"), TERM } ;
    TERM = FACTOR, { ("*" | "/"), FACTOR } ;
    FACTOR = ("+" | "-") FACTOR | "(" EXPRESSION ")" | number ;
