# 🚀 Deploy do Dashboard AICockpit na AWS EC2

## 📋 Pré-requisitos

### 1. Conta AWS
- Conta AWS ativa
- Acesso ao console AWS
- Chave de acesso (Access Key) e Secret Key

### 2. Arquivos Locais
- Dashboard AICockpit completo
- Arquivo `requirements.txt`
- Configurações do projeto

## 🏗️ Passo 1: Criar Instância EC2

### 1.1 Acessar Console AWS
1. Faça login no [Console AWS](https://console.aws.amazon.com)
2. Navegue para **EC2** > **Instances**
3. Clique em **Launch Instance**

### 1.2 Configurar Instância
```
Nome: AICockpit-Dashboard
AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
Instance Type: t2.micro (Free tier eligible)
Key Pair: Criar nova ou usar existente
Security Group: Criar novo com as seguintes regras:
  - SSH (22) - Seu IP
  - HTTP (80) - 0.0.0.0/0
  - HTTPS (443) - 0.0.0.0/0
  - Custom TCP (8501) - 0.0.0.0/0  # Porta do Streamlit
Storage: 8 GB (Free tier)
```

### 1.3 Lançar Instância
1. Clique em **Launch Instance**
2. Aguarde a instância ficar **Running**
3. Anote o **Public IP** da instância

## 🔧 Passo 2: Conectar à Instância

### 2.1 Conectar via SSH
```bash
# Windows (usando Git Bash ou WSL)
ssh -i "sua-chave.pem" ubuntu@SEU-IP-PUBLICO

# Linux/Mac
ssh -i "sua-chave.pem" ubuntu@SEU-IP-PUBLICO
```

### 2.2 Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

## 🐍 Passo 3: Instalar Python e Dependências

### 3.1 Instalar Python 3.9+
```bash
sudo apt install python3 python3-pip python3-venv -y
python3 --version  # Verificar versão
```

### 3.2 Instalar Git
```bash
sudo apt install git -y
```

## 📁 Passo 4: Transferir Arquivos

### Opção A: Upload via SCP (Recomendado)
```bash
# No seu computador local
scp -i "sua-chave.pem" -r /caminho/para/AICockpitDashboard ubuntu@SEU-IP-PUBLICO:~/
```

### Opção B: Git Clone (se tiver repositório)
```bash
# Na instância EC2
git clone https://github.com/seu-usuario/AICockpitDashboard.git
cd AICockpitDashboard
```

### Opção C: Upload Manual
1. Compacte o projeto local: `zip -r dashboard.zip AICockpitDashboard/`
2. Use FileZilla ou WinSCP para transferir
3. Na EC2: `unzip dashboard.zip`

## 🛠️ Passo 5: Configurar Ambiente

### 5.1 Criar Ambiente Virtual
```bash
cd AICockpitDashboard
python3 -m venv venv
source venv/bin/activate
```

### 5.2 Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 Configurar Credenciais
```bash
# Copiar template de configuração
cp config_template.py config/settings.py

# Editar configurações
nano config/settings.py
```

**Configurar no arquivo `config/settings.py`:**
```python
# Suas credenciais Jira
JIRA_EMAIL = "lidinei@compasso.com.br"
\ = ""
```

## 🚀 Passo 6: Executar Dashboard

### 6.1 Teste Local
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar dashboard
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 6.2 Verificar Funcionamento
1. Abra navegador: `http://SEU-IP-PUBLICO:8501`
2. Teste login com suas credenciais
3. Verifique se todas as abas funcionam

## 🔒 Passo 7: Configurar Execução Contínua

### 7.1 Instalar Screen (Para manter rodando)
```bash
sudo apt install screen -y
```

### 7.2 Executar em Background
```bash
# Criar sessão screen
screen -S dashboard

# Ativar ambiente e executar
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Pressionar Ctrl+A, depois D para "detach"
```

### 7.3 Reconectar à Sessão
```bash
# Listar sessões
screen -ls

# Reconectar
screen -r dashboard
```

## 🌐 Passo 8: Configurar Nginx (Opcional - Produção)

### 8.1 Instalar Nginx
```bash
sudo apt install nginx -y
```

### 8.2 Configurar Proxy Reverso
```bash
sudo nano /etc/nginx/sites-available/dashboard
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name SEU-IP-PUBLICO;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.3 Ativar Configuração
```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔄 Passo 9: Configurar Systemd (Serviço Automático)

### 9.1 Criar Arquivo de Serviço
```bash
sudo nano /etc/systemd/system/dashboard.service
```

**Conteúdo do arquivo:**
```ini
[Unit]
Description=AICockpit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AICockpitDashboard
Environment=PATH=/home/ubuntu/AICockpitDashboard/venv/bin
ExecStart=/home/ubuntu/AICockpitDashboard/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9.2 Ativar Serviço
```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
sudo systemctl status dashboard.service
```

### 9.3 Comandos Úteis do Serviço
```bash
# Parar serviço
sudo systemctl stop dashboard.service

# Reiniciar serviço
sudo systemctl restart dashboard.service

# Ver logs
sudo journalctl -u dashboard.service -f
```

## 🔐 Passo 10: Configurar HTTPS (Opcional)

### 10.1 Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 10.2 Obter Certificado SSL
```bash
# Substitua pelo seu domínio
sudo certbot --nginx -d seu-dominio.com
```

## 📊 Passo 11: Monitoramento

### 11.1 Verificar Recursos
```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Processos do Streamlit
ps aux | grep streamlit
```

### 11.2 Logs do Dashboard
```bash
# Logs do systemd
sudo journalctl -u dashboard.service -n 50

# Logs do Nginx (se configurado)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🚨 Troubleshooting

### Problema: Dashboard não carrega
```bash
# Verificar se o serviço está rodando
sudo systemctl status dashboard.service

# Verificar logs
sudo journalctl -u dashboard.service -f

# Testar manualmente
cd AICockpitDashboard
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Problema: Erro de conexão Jira
```bash
# Verificar configurações
cat config/settings.py

# Testar conectividade
ping compasso.atlassian.net

# Verificar credenciais no browser
curl -u "email:api_key" https://compasso.atlassian.net/rest/api/2/myself
```

### Problema: Porta 8501 não acessível
```bash
# Verificar Security Group na AWS
# Verificar se a porta está aberta
sudo ufw status
sudo ufw allow 8501

# Verificar se o Streamlit está ouvindo
netstat -tlnp | grep 8501
```

## 💰 Custos AWS (Estimativa)

### Free Tier (12 meses)
- **EC2 t2.micro**: Gratuito (750 horas/mês)
- **Storage**: 30 GB gratuitos
- **Data Transfer**: 15 GB gratuitos/mês

### Após Free Tier
- **EC2 t2.micro**: ~$8.50/mês
- **Storage EBS**: ~$0.10/GB/mês
- **Data Transfer**: $0.09/GB (após 15GB)

## 📝 Resumo dos URLs

### Acesso ao Dashboard
```
# Direto (porta 8501)
http://SEU-IP-PUBLICO:8501

# Com Nginx (porta 80)
http://SEU-IP-PUBLICO

# Com HTTPS (se configurado)
https://seu-dominio.com
```

### Comandos Essenciais
```bash
# SSH na instância
ssh -i "sua-chave.pem" ubuntu@SEU-IP-PUBLICO

# Verificar status do serviço
sudo systemctl status dashboard.service

# Ver logs em tempo real
sudo journalctl -u dashboard.service -f

# Reiniciar dashboard
sudo systemctl restart dashboard.service
```

## ✅ Checklist Final

- [ ] Instância EC2 criada e rodando
- [ ] Security Group configurado (portas 22, 80, 443, 8501)
- [ ] SSH funcionando
- [ ] Python e dependências instaladas
- [ ] Arquivos do dashboard transferidos
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Configurações do Jira definidas
- [ ] Dashboard testado manualmente
- [ ] Serviço systemd configurado
- [ ] Dashboard acessível via browser
- [ ] Todas as abas funcionando
- [ ] Login com credenciais Jira OK

## 🎯 Próximos Passos

1. **Backup Regular**: Configure backup dos dados
2. **Monitoramento**: Implemente alertas de sistema
3. **Domínio**: Configure um domínio personalizado
4. **SSL**: Configure certificado HTTPS
5. **Load Balancer**: Para alta disponibilidade (opcional)

## 📞 Suporte

### Logs Importantes
```bash
# Dashboard logs
sudo journalctl -u dashboard.service -n 100

# System logs
sudo tail -f /var/log/syslog

# Nginx logs (se usado)
sudo tail -f /var/log/nginx/error.log
```

### Comandos de Diagnóstico
```bash
# Verificar recursos
htop
df -h
free -h

# Verificar rede
netstat -tlnp | grep 8501
ss -tlnp | grep 8501

# Verificar processos
ps aux | grep streamlit
ps aux | grep python
```

---

**🚀 Dashboard AICockpit pronto para produção na AWS EC2!**

**URL de Acesso:** `http://SEU-IP-PUBLICO:8501`
**Login:** Suas credenciais Jira configuradas
**Funcionalidades:** 6 abas completas (Overview, Bugs, Incidents, Priorities, Quarters, Gantt)
