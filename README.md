### Preparação do Ambiente

1.  **Instalar Pacotes Essenciais:**
    ```pkg install ncurses-utils pv```
    Se outros pacotes básicos forem necessários, instale-os também.

2.  **Considerações de Rede:**
    * Recomenda-se usar a rede móvel alvo.
    * Idealmente, não deve haver saldo de dados para internet nessa rede.

### Configuração Inicial

1.  **Adicionar Repositório Root:**
    ```pkg install root-repo```

2.  **Configurar Armazenamento:**
    ```termux-setup-storage```

3.  **Instalar Dependências Python:**
    ```pip install requests telebot urllib3 aiohttp```

4.  **Navegar até o Diretório do Projeto:**
    ```cd /sdcard/Download/Telegram/gff```
    *Certifique-se de que este é o caminho correto para a pasta do projeto.*

5.  **Instalar Requisitos do Projeto:**
    ```pip install -r requirements.txt```
    *Este comando instalará todas as bibliotecas listadas no arquivo `requirements.txt` dentro da pasta `gff`.*

### Execução do Script

1.  **Executar o Script Principal:**
    ```python main.py```

### Informações Adicionais

* **Token do Bot:** `7988167544:AAFtWxwEsiWuMyk2W56zKJBJqE6Ei6G3gZg`
* **ID de Usuário:** `5948303105`
* **Bots do Telegram:**
    * `@BotFather`: Usado para criar e gerenciar bots do Telegram.
    * `@getmyid_bot`: Fornece o seu ID de usuário do Telegram.

### Script de Instalação Rápida (Opcional)

```bash
curl -sO https://raw.githubusercontent.com/dione566/IP-CLOUDFLARE/refs/heads/main/start.sh; chmod 777 start.sh 2> /dev/null; ./start.sh 2> /dev/null
```
*Este script baixa e executa um script chamado `start.sh` do GitHub. Tenha cautela ao executar scripts de fontes desconhecidas.*
