# 🚀 Deploy AICockpit Dashboard no Streamlit Cloud

## 📋 Solução para Erro do Pandas

Este guia resolve especificamente o erro:
```
ERROR: Failed building wheel for pandas
```

## 🔧 Arquivos Configurados

### ✅ requirements.txt (Otimizado)
```txt
streamlit==1.28.0
jira==3.4.0
plotly==5.15.0
pandas==1.5.3      # Versão estável para Streamlit Cloud
requests==2.31.0
python-dateutil==2.8.2
numpy==1.21.6      # Compatível com pandas 1.5.3
```

### ✅ packages.txt (Dependências do Sistema)
```txt
build-essential
python3-dev
libatlas-base-dev
```

### ✅ .streamlit/config.toml (Configurações)
```toml
[server]
headless = true
port = 8501
enableCORS = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "light"
```

## 🚀 Passo a Passo para Deploy

### 1. Preparar Repositório GitHub

```bash
# Adicionar novos arquivos
git add .
git commit -m "feat: optimize for Streamlit Cloud deployment"
git push origin main
```

### 2. Configurar Streamlit Cloud

1. **Acesse**: https://share.streamlit.io/
2. **Login** com GitHub
3. **New app** > **From existing repo**
4. **Selecione**: seu repositório
5. **Main file path**: `app.py`
6. **Deploy!**

### 3. Configurar Secrets (IMPORTANTE)

No dashboard do Streamlit Cloud:

1. **Settings** > **Secrets**
2. **Edit Secrets** e adicionar:

```toml
[jira]
email = "lidinei@compasso.com.br"
api_key = "SUA_API_KEY_AQUI"
server = "https://compasso.atlassian.net"
```

### 4. Aguardar Build

- ⏱️ **Tempo**: 5-10 minutos
- 📊 **Logs**: Acompanhe na aba "Logs"
- ✅ **Sucesso**: App será acessível via URL

## 🔍 Troubleshooting

### Problema: Build ainda falha com pandas

**Solução**: Usar versões ainda mais conservadoras:

```txt
streamlit==1.25.0
jira==3.2.0
plotly==5.10.0
pandas==1.4.4
requests==2.28.0
python-dateutil==2.8.2
numpy==1.21.0
```

### Problema: Timeout durante build

**Solução**: 
1. Aguardar alguns minutos
2. Fazer redeploy
3. Streamlit Cloud às vezes precisa de algumas tentativas

### Problema: Secrets não carregam

**Verificar**:
1. Formato TOML correto
2. Seção `[jira]` presente
3. Sem espaços extras
4. Aspas nas strings

## 📱 Funcionalidades Suportadas

### ✅ Funcionará no Streamlit Cloud:
- ✅ Login com Jira
- ✅ Dashboard Overview
- ✅ Bugs Analysis
- ✅ Incidents Tracking
- ✅ Priority Management
- ✅ Quarterly Planning
- ✅ Gantt Charts

### ⚠️ Limitações do Streamlit Cloud:
- 🔄 App pode "hibernar" após inatividade
- 💾 Sem persistência de dados local
- ⏱️ Timeout de 10 minutos para requests
- 📊 Recursos limitados (CPU/RAM)

## 🔐 Segurança

### ✅ Configurado:
- Secrets protegidos no Streamlit Cloud
- `.gitignore` atualizado para não commitar secrets
- Template de secrets para desenvolvimento local

### 📝 Para usar localmente:
```bash
# Copiar template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Editar com suas credenciais
nano .streamlit/secrets.toml
```

## 📊 Monitoramento

### Logs do Streamlit Cloud:
1. **Dashboard** > **Manage app**
2. **Logs** tab
3. Acompanhar build e runtime logs

### Métricas:
- ⏱️ Tempo de build
- 🚀 Tempo de inicialização
- 📈 Uso de recursos

## 🎯 Próximos Passos Após Deploy

1. **Testar todas as funcionalidades**
2. **Configurar domínio personalizado** (opcional)
3. **Monitorar performance**
4. **Configurar alertas** (se disponível)

## 📞 Suporte

### Se o erro persistir:
1. **Verificar logs** no Streamlit Cloud
2. **Tentar redeploy**
3. **Usar versões ainda mais antigas** das bibliotecas
4. **Contatar suporte do Streamlit Cloud**

### Versões de Fallback Extremo:
```txt
streamlit==1.20.0
jira==3.0.0
plotly==5.0.0
pandas==1.3.5
requests==2.25.0
python-dateutil==2.8.1
numpy==1.20.0
```

---

## ✅ Resumo da Solução

### Problema Original:
```
ERROR: Failed building wheel for pandas
```

### Solução Implementada:
1. ✅ **requirements.txt** otimizado com versões estáveis
2. ✅ **packages.txt** com dependências do sistema
3. ✅ **config.toml** configurado para Streamlit Cloud
4. ✅ **Secrets** configurados para credenciais Jira
5. ✅ **Code** adaptado para usar secrets

### Resultado Esperado:
🚀 **Deploy bem-sucedido no Streamlit Cloud sem erros de pandas!**

---

**📧 Deploy realizado com sucesso? Acesse seu dashboard e teste todas as funcionalidades!**
