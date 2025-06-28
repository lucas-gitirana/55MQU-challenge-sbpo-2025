import sys
import random
import time
from collections import defaultdict
from classes import Pedido, Corredor


# =============================
# LEITURA DAS INSTÂNCIAS
# =============================
def ler_instancias(path):
    with open(path) as f:
        o, i, a = map(int, f.readline().split())

        pedidos = []
        for pid in range(o):
            parts = list(map(int, f.readline().split()))
            itens = [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]
            pedido_obj = Pedido(pid, itens)
            pedido_obj.total_unidades = sum(q for _, q in itens)  # pré-cálculo
            pedidos.append(pedido_obj)

        corredores = []
        for cid in range(a):
            parts = list(map(int, f.readline().split()))
            itens = [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]
            corredor_obj = Corredor(cid, itens)
            corredor_obj.total_unidades = sum(q for _, q in itens)
            corredores.append(corredor_obj)

        lb, ub = map(int, f.readline().split())

        return pedidos, corredores, lb, ub


# =============================
# FUNÇÕES AUXILIARES
# =============================
def avaliar(pedidos_bin, pedidos, corredores_wave):
    total = sum(
        pedidos[pid].total_unidades
        for pid, included in enumerate(pedidos_bin) if included
    )
    n_corr = len(corredores_wave)
    if n_corr == 0:
        return 0
    return total / n_corr


def determinar_corredores(pedidos_bin, pedidos, corredores, start_time=None, max_tempo_segundos=None):
    demanda = defaultdict(int)
    for pid, included in enumerate(pedidos_bin):
        if included:
            for i, q in pedidos[pid].itens.items():
                if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
                    return None
                demanda[i] += q

    corredores_ids = list(range(len(corredores)))
    random.shuffle(corredores_ids)

    fornecimento = defaultdict(int)
    usados = []

    for cid in corredores_ids:
        if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
            return None

        c = corredores[cid]
        usados.append(cid)
        for i, q in c.itens.items():
            if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
                return None
            fornecimento[i] += q

        if all(demanda[i] <= fornecimento[i] for i in demanda):
            return usados

    return None


# =============================
# SOLUÇÃO INICIAL
# =============================
def gerar_solucao_inicial(pedidos, corredores, lb, ub, start_time=None, max_tempo_segundos=None, tentativas_max=1000):
    for _ in range(tentativas_max):
        if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
            return None, None

        pedidos_ids = list(range(len(pedidos)))
        random.shuffle(pedidos_ids)
        pedidos_bin = [0] * len(pedidos)
        total_unidades = 0

        for pid in pedidos_ids:
            unidades = pedidos[pid].total_unidades
            if total_unidades + unidades > ub:
                continue
            pedidos_bin[pid] = 1
            total_unidades += unidades
            if total_unidades >= lb:
                break

        if total_unidades < lb:
            continue

        corredores_wave = determinar_corredores(pedidos_bin, pedidos, corredores, start_time, max_tempo_segundos)
        if corredores_wave is not None:
            return pedidos_bin, corredores_wave

    return None, None


# =============================
# PERTURBAR
# =============================
def perturbar(pedidos_bin, pedidos, lb, ub, intensidade=0.2, respeita_lb_durante_adicao=True):
    pedidos_novo = pedidos_bin[:]
    indices_in = [i for i, v in enumerate(pedidos_novo) if v == 1]
    indices_out = [i for i, v in enumerate(pedidos_novo) if v == 0]

    if len(indices_in) == 0:
        return pedidos_novo

    n_remover = max(1, int(len(indices_in) * intensidade))
    remover = random.sample(indices_in, min(n_remover, len(indices_in)))
    for r in remover:
        pedidos_novo[r] = 0

    total = sum(
        pedidos[pid].total_unidades
        for pid, included in enumerate(pedidos_novo) if included
    )

    random.shuffle(indices_out)
    for c in indices_out:
        unidades = pedidos[c].total_unidades
        if total + unidades <= ub:
            pedidos_novo[c] = 1
            total += unidades
            if respeita_lb_durante_adicao and total >= lb:
                break

    if total < lb:
        return perturbar(pedidos_bin, pedidos, lb, ub, intensidade, respeita_lb_durante_adicao)

    return pedidos_novo


# =============================
# BUSCA LOCAL
# =============================
def busca_local(pedidos_bin, pedidos, corredores, lb, ub, start_time=None, max_tempo_segundos=None, max_vizinhanca=1000):
    pedidos_atual = pedidos_bin[:]
    melhor_corredores = determinar_corredores(pedidos_atual, pedidos, corredores, start_time, max_tempo_segundos)
    if melhor_corredores is None:
        return pedidos_atual, None
    melhor_obj = avaliar(pedidos_atual, pedidos, melhor_corredores)

    melhorou = True
    iter_viz = 0

    indices_in = [i for i, v in enumerate(pedidos_atual) if v == 1]
    indices_out = [i for i, v in enumerate(pedidos_atual) if v == 0]

    while melhorou and iter_viz < max_vizinhanca:
        if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
            break

        melhorou = False

        for p_out in indices_in:
            if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
                return pedidos_atual, melhor_corredores
            for p_in in indices_out:
                if start_time and max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
                    return pedidos_atual, melhor_corredores

                pedidos_atual[p_out] = 0
                pedidos_atual[p_in] = 1

                total = sum(pedidos[pid].total_unidades for pid, included in enumerate(pedidos_atual) if included)
                if total < lb or total > ub:
                    pedidos_atual[p_out] = 1
                    pedidos_atual[p_in] = 0
                    continue

                corredores_tentativa = determinar_corredores(pedidos_atual, pedidos, corredores, start_time, max_tempo_segundos)
                if corredores_tentativa is None:
                    pedidos_atual[p_out] = 1
                    pedidos_atual[p_in] = 0
                    continue

                obj = avaliar(pedidos_atual, pedidos, corredores_tentativa)

                if obj > melhor_obj:
                    melhor_corredores = corredores_tentativa
                    melhor_obj = obj
                    melhorou = True
                    indices_in = [i for i, v in enumerate(pedidos_atual) if v == 1]
                    indices_out = [i for i, v in enumerate(pedidos_atual) if v == 0]
                    break
                else:
                    pedidos_atual[p_out] = 1
                    pedidos_atual[p_in] = 0

            if melhorou:
                break

        iter_viz += 1

    return pedidos_atual, melhor_corredores


# =============================
# ILS
# =============================
def ils(pedidos, corredores, lb, ub, max_iter=10000, max_tempo_segundos=None,
        intensidade_perturbacao=0.2, respeita_lb_durante_adicao=True):

    start_time = time.time()

    pedidos_bin, corredores_wave = gerar_solucao_inicial(pedidos, corredores, lb, ub, start_time, max_tempo_segundos)
    if pedidos_bin is None:
        print("Não foi possível gerar solução inicial dentro do tempo limite.")
        return None, None

    melhor_obj = avaliar(pedidos_bin, pedidos, corredores_wave)
    melhor_solucao = (pedidos_bin, corredores_wave)

    for _ in range(max_iter):
        if max_tempo_segundos and (time.time() - start_time >= max_tempo_segundos):
            print(f"Tempo limite atingido em ILS: {time.time() - start_time:.2f} segundos.")
            break

        pedidos_perturbados = perturbar(pedidos_bin, pedidos, lb, ub,
                                         intensidade=intensidade_perturbacao,
                                         respeita_lb_durante_adicao=respeita_lb_durante_adicao)

        corredores_perturbados = determinar_corredores(pedidos_perturbados, pedidos, corredores, start_time, max_tempo_segundos)
        if corredores_perturbados is None:
            continue

        pedidos_local, corredores_local = busca_local(
            pedidos_perturbados, pedidos, corredores, lb, ub, start_time, max_tempo_segundos
        )
        if corredores_local is None:
            continue

        obj = avaliar(pedidos_local, pedidos, corredores_local)

        if obj > melhor_obj:
            melhor_solucao = (pedidos_local[:], corredores_local[:])
            melhor_obj = obj
            pedidos_bin, corredores_wave = pedidos_local[:], corredores_local[:]

    return melhor_solucao


# =============================
# SALVAR SAÍDA
# =============================
def salvar_saida(output_path, pedidos_bin, corredores_wave):
    pedidos_wave = [i for i, v in enumerate(pedidos_bin) if v == 1]
    with open(output_path, 'w') as f:
        f.write(f"{len(pedidos_wave)}\n")
        for p in pedidos_wave:
            f.write(f"{p}\n")
        f.write(f"{len(corredores_wave)}\n")
        for c in corredores_wave:
            f.write(f"{c}\n")


# =============================
# EXECUÇÃO
# =============================
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python solver.py <arquivo_entrada> <arquivo_saida> <intensidade_perturbacao> <respeita_lb_durante_adicao>")
        print("Exemplo: python solver.py instancia.txt saida.txt 0.2 True")
        sys.exit(1)

    arquivo_instancia = sys.argv[1]
    arquivo_saida = sys.argv[2]
    intensidade_perturbacao = float(sys.argv[3])
    respeita_lb_durante_adicao = sys.argv[4].lower() in ["true", "1", "t", "yes", "y"]

    pedidos, corredores, lb, ub = ler_instancias(arquivo_instancia)
    LIMITE_TEMPO = 60  # segundos

    pedidos_wave, corredores_wave = ils(
        pedidos,
        corredores,
        lb,
        ub,
        max_iter=10000,
        max_tempo_segundos=LIMITE_TEMPO,
        intensidade_perturbacao=intensidade_perturbacao,
        respeita_lb_durante_adicao=respeita_lb_durante_adicao
    )

    if pedidos_wave is None or corredores_wave is None:
        print("Não foi possível encontrar solução dentro do tempo limite.")
        sys.exit(1)

    salvar_saida(arquivo_saida, pedidos_wave, corredores_wave)

    print('Pedidos selecionados:', [i for i, v in enumerate(pedidos_wave) if v == 1])
    print('Corredores selecionados:', corredores_wave)
    print('F.O.:', avaliar(pedidos_wave, pedidos, corredores_wave))
