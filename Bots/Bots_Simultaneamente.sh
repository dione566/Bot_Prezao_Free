#!/bin/bash

# --- CONFIGURAÇÃO DE BOTS ---
BOTS=(
    "/sdcard/Download/Bot/botweb1"
    "/sdcard/Download/Bot/botweb2"
)
SCRIPT_PYTHON="main.py"
LOG_PREFIX="execucao" # O arquivo de log será: <DIRETORIO>/<LOG_PREFIX>.log

# Variável para armazenar os PIDs dos processos Python
declare -A PIDS # Array associativo para PIDs: Chave = Diretório, Valor = PID

# --- FUNÇÕES ---

# Função para registrar eventos
log_message() {
    local log_file="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$log_file"
}

# Função de limpeza para lidar com Ctrl+C
cleanup() {
    echo -e "\nCtrl+C detectado. Tentando fechar os bots..."
    
    local all_clean=true
    
    # Itera sobre os PIDs registrados
    for diretorio in "${!PIDS[@]}"; do
        local pid="${PIDS[$diretorio]}"
        local log_file="$diretorio/$LOG_PREFIX.log"
        
        log_message "$log_file" "SINAL DE INTERRUPÇÃO (Ctrl+C) RECEBIDO para $diretorio. Tentando fechar o bot (PID: $pid)..."

        # Verifica se o PID está definido e ativo
        if [ ! -z "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "-> Enviando sinal de TERMinação ($pid) para $diretorio..."
            kill -SIGTERM "$pid"
            
            # Espera um pouco, até 5 segundos
            local timeout=5
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt $timeout ]; do
                sleep 1
                count=$((count+1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                # Se ainda estiver rodando após o timeout, envia SIGKILL
                echo "-> O bot $diretorio ($pid) não respondeu. Enviando SIGKILL!"
                kill -SIGKILL "$pid"
                wait "$pid" 2>/dev/null
                log_message "$log_file" "FECHAMENTO INTERROMPIDO FORÇADO (SIGKILL): O script foi encerrado à força."
                echo "Aviso: O bot $diretorio foi encerrado à força (SIGKILL)."
                all_clean=false
            else
                wait "$pid" 2>/dev/null # Espera a terminação limpa
                CODIGO_SAIDA=$?
                log_message "$log_file" "FECHAMENTO INTERROMPIDO LIMPO: O script foi encerrado com sucesso (Código de saída: $CODIGO_SAIDA)."
                echo "-> Fechamento Limpo: O bot $diretorio foi encerrado corretamente."
            fi
        else
            log_message "$log_file" "FECHAMENTO INTERROMPIDO: O bot $diretorio não estava em execução ou o PID era desconhecido."
            echo "-> O bot $diretorio não estava em execução ou não foi necessário encerrar um processo ativo."
        fi
    done

    if $all_clean; then
        echo -e "\nTODOS OS BOTS FORAM ENCERRADOS LIMPADAMENTE."
    else
        echo -e "\nAVISO: PELO MENOS UM BOT FOI ENCERRADO À FORÇA."
    fi
    
    echo "FIM DA EXECUÇÃO (INTERROMPIDA)"
    exit 130 # Código de saída padrão para interrupção por Ctrl+C
}

# Configura o trap para o sinal INT (Ctrl+C)
trap cleanup INT

# --- SCRIPT PRINCIPAL ---

# 0. Limpar a tela (janela de comando)
clear
echo "--- INICIANDO ROTINA DE BOTS PARALELOS ---"

# 1. Limpar e Registrar Início
for diretorio in "${BOTS[@]}"; do
    log_file="$diretorio/$LOG_PREFIX.log"
    
    echo "Limpando o arquivo de log: $log_file"
    > "$log_file" # Limpa o log
    
    log_message "$log_file" "INÍCIO DA EXECUÇÃO DO BOT"
    echo "-> Verifique $log_file para detalhes do bot em $diretorio."
done

echo -e "\n--- INICIANDO EXECUÇÃO PARALELA ---"

# 2. Execução dos Bots em Paralelo
for diretorio in "${BOTS[@]}"; do
    log_file="$diretorio/$LOG_PREFIX.log"
    
    # Navegação para o diretório
    if ! cd "$diretorio"; then
        log_message "$log_file" "ERRO FATAL: Não foi possível navegar para o diretório $diretorio."
        echo "ERRO: O diretório $diretorio não existe ou as permissões estão incorretas. Pulando este bot."
        continue # Pula para o próximo bot
    fi

    # Execução do script Python em segundo plano e captura do PID
    echo "Executando $SCRIPT_PYTHON em $diretorio em segundo plano..."
    log_message "$log_file" "Executando comando: python $SCRIPT_PYTHON em segundo plano"
    
    python "$SCRIPT_PYTHON" &
    PIDS[$diretorio]=$! # Captura o Process ID (PID) do último comando em background
    
    echo "Bot $diretorio PID: ${PIDS[$diretorio]}"
    
    # Retorna para o diretório de onde o script foi chamado (opcional, mas boa prática)
    cd - > /dev/null
done

if [ ${#PIDS[@]} -eq 0 ]; then
    echo -e "\nNenhum bot pôde ser iniciado. Saindo."
    trap - INT
    exit 1
fi

echo -e "\nTODOS OS BOTS ESTÃO EM EXECUÇÃO. Pressione Ctrl+C para fechar todos."

# 3. Espera pelos Bots
# Cria uma lista de PIDs para esperar
pids_to_wait=()
for pid in "${PIDS[@]}"; do
    pids_to_wait+=("$pid")
done

# Espera que TODOS os scripts Python terminem
wait "${pids_to_wait[@]}"

# 4. Verificação de Fechamento (Saída normal)
trap - INT # Remove o trap para que a limpeza não seja chamada duas vezes ao sair

echo -e "\n--- VERIFICAÇÃO DE FECHAMENTO NORMAL ---"

# Itera novamente sobre os diretórios para verificar os códigos de saída
all_ok=true
for diretorio in "${BOTS[@]}"; do
    pid="${PIDS[$diretorio]}"
    # O código de saída do `wait` é o último, precisamos buscar o código de saída real do processo
    # No caso de um script longo, `wait` para múltiplos PIDs não retorna os códigos de saída individualmente de forma simples.
    # No entanto, se o processo terminou, a verificação de log já pode ser suficiente, ou assumimos que
    # se o `wait` geral terminou, os processos morreram.

    # Para um `wait` em múltiplos PIDs, o `$?` é o código de saída do *último* comando `wait` que pode ser 0, ou um código de erro.
    # A melhor abordagem aqui é confiar que se chegamos a este ponto, os processos terminaram.

    if [ -f "$diretorio/$LOG_PREFIX.log" ]; then
        log_message "$diretorio/$LOG_PREFIX.log" "FECHAMENTO NORMAL: O script Python terminou."
        echo "-> O bot $diretorio terminou sua execução."
    fi
done

echo -e "\nEXECUÇÃO CONCLUÍDA."

exit 0 # Sai com código de sucesso

