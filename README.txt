==============================================================
INSTRUÇÕES DE COMPILAÇÃO E EXECUÇÃO
==============================================================

Projeto: Resolução do Problema da Seleção de Pedidos Ótima via ILS  
Autores: Erick Augusto Warmling; Lucas Emanoel Gitirana; Marco Antonio Garlini Possamai  
Linguagem: Python  
--------------------------------------------------------------

1. PRÉ-REQUISITOS
------------------------------
- Python 3.8 ou superior instalado

2. SOBRE O PROJETO
------------------------------
Este projeto é uma implementação do algoritmo ILS (Iterated Local Search) para o Problema da Seleção de Pedidos Ótima. Ele foi desenvolvido com base em um framework inicial e expandido com novos arquivos e algoritmos para atender aos requisitos do desafio.

A estrutura principal do código está contida na pasta `challenge-sbpo-2025/`, onde foram integrados os arquivos desenvolvidos pela equipe.

Arquivos principais:
- `solver.py`         → Algoritmo principal
- `classes.py`        → Definição das classes Pedido e Corredor

3. EXECUÇÃO
------------------------------
Para executar o algoritmo, abra o terminal e digite:

    cd challenge-sbpo-2025
    python solver.py <arquivo_entrada> <arquivo_saida> <intensidade> <respeita_lb>

Parâmetros:
- `<arquivo_entrada>`   → caminho do arquivo da instância (ex: `datasets/a/instance_0020.txt`)
- `<arquivo_saida>`     → nome do arquivo onde será gravada a solução (ex: `output.txt`)
- `<intensidade>`       → valor entre 0 e 1 que define a fração de pedidos a remover na perturbação
- `<respeita_lb>`       → `True` ou `False`, indica se o LB deve ser respeitado durante a adição de pedidos

Exemplo:

    python solver.py datasets/a/instance_0020.txt output.txt 0.2 True

4. FORMATO DE SAÍDA
------------------------------
O arquivo de saída gerado seguirá o formato exigido pelo desafio:

    <número de pedidos selecionados>
    <id do pedido 1>
    ...
    <id do pedido n>
    <número de corredores selecionados>
    <id do corredor 1>
    ...
    <id do corredor m>

5. VALIDAÇÃO COM CHECKER DO DESAFIO
------------------------------
Para verificar se a solução está correta, utilize o script `checker.py`:

    python checker.py datasets/a/instance_0020.txt output.txt

6. TEMPO DE EXECUÇÃO
------------------------------
O algoritmo possui um tempo limite de execução configurado em 60 segundos.  
Esse valor pode ser alterado diretamente no arquivo `solver.py`, na linha:

    LIMITE_TEMPO = 60

==============================================================
