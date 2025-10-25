#!/bin/bash

# --- CONFIGURAÇÃO ---
DIRETORIO="/sdcard/Download/Bot/botweb1"
SCRIPT_PYTHON="main.py"
LOG_ARQUIVO="$DIRETORIO/execucao.log"

# Variável para armazenar o PID do processo Python
PID_PYTHON=""

# Função para registrar eventos
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_ARQUIVO"
}

# Função de limpeza para lidar com Ctrl+C
cleanup() {
    log_message "SINAL DE INTERRUPÇÃO (Ctrl+C) RECEBIDO. Tentando fechar o bot..."
    echo -e "\nCtrl+C detectado. Tentando fechar o bot..."

    # Verifica se o PID do processo Python está definido e ativo
    if [ ! -z "$PID_PYTHON" ] && kill -0 "$PID_PYTHON" 2>/dev/null; then
        echo "Enviando sinal de TERMinação ($PID_PYTHON) para o script Python..."
        kill -SIGTERM "$PID_PYTHON"
        wait "$PID_PYTHON" 2>/dev/null # Espera que o processo termine
        CODIGO_SAIDA=$?

        if [ $CODIGO_SAIDA -eq 0 ]; then
            log_message "FECHAMENTO INTERROMPIDO LIMPO: O script Python foi encerrado com sucesso."
            echo "Fechamento Limpo: O bot foi encerrado corretamente."
        else
            log_message "FECHAMENTO INTERROMPIDO COM ERRO: O script Python foi encerrado (Código de saída: $CODIGO_SAIDA)."
            echo "Aviso: O bot foi encerrado (Código de saída: $CODIGO_SAIDA)."
        fi
    else
        log_message "FECHAMENTO INTERROMPIDO: O bot não estava em execução ou o PID era desconhecido."
        echo "O bot não estava em execução ou não foi necessário encerrar um processo ativo."
    fi

    log_message "FIM DA EXECUÇÃO DA ROTINA (INTERROMPIDA)"
    exit 130 # Código de saída padrão para interrupção por Ctrl+C
}

# Configura o trap para o sinal INT (Ctrl+C)
trap cleanup INT

# --- SCRIPT PRINCIPAL ---

# 1. Registro de Início
log_message "INÍCIO DA EXECUÇÃO DO BOT"
echo "Iniciando a rotina... (Verifique $LOG_ARQUIVO para detalhes)"

# 2. Navegação para o diretório
cd "$DIRETORIO"

if [ $? -ne 0 ]; then
    log_message "ERRO FATAL: Não foi possível navegar para o diretório $DIRETORIO."
    echo "ERRO: O diretório não existe ou as permissões estão incorretas."
    # Remove o trap antes de sair para evitar chamada dupla de cleanup
    trap - INT
    exit 1 # Sai com código de erro
fi

# 3. Execução do script Python em segundo plano e captura do PID
echo "Executando $SCRIPT_PYTHON em segundo plano..."
log_message "Executando comando: python $SCRIPT_PYTHON em segundo plano"
python "$SCRIPT_PYTHON" &
PID_PYTHON=$! # Captura o Process ID (PID) do último comando em background

echo "Bot PID: $PID_PYTHON. Pressione Ctrl+C para fechar."

# Espera que o script Python termine
wait "$PID_PYTHON"
CODIGO_SAIDA=$?

# 4. Verificação de Fechamento (Saída normal)
# Remove o trap para que a limpeza não seja chamada duas vezes ao sair
trap - INT

if [ $CODIGO_SAIDA -eq 0 ]; then
    log_message "FECHAMENTO LIMPO: O script Python ($SCRIPT_PYTHON) foi concluído com sucesso."
    echo "Sucesso: O bot foi executado e encerrado (Código de saída: 0)."
else
    log_message "FECHAMENTO COM ERRO: O script Python ($SCRIPT_PYTHON) falhou (Código de saída: $CODIGO_SAIDA)."
    echo "AVISO: O bot terminou com um erro (Código de saída: $CODIGO_SAIDA)."
fi

# 5. Registro de Fim
log_message "FIM DA EXECUÇÃO DA ROTINA"

exit 0 # Sai do script Bash com sucesso
