# 🧪 Guia de Teste Completo - Conheces Alguém?

## 🚀 Como Iniciar

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Iniciar PostgreSQL (se não estiver rodando)
docker-compose up -d db

# 3. Rodar servidor
python manage.py runserver
```

Acesse: **http://localhost:8000**

---

## ✅ Checklist de Testes

### 1. **Homepage** 
- [ ] Página carrega corretamente
- [ ] Barra de busca está visível
- [ ] Categorias aparecem em linha horizontal
- [ ] Clique em categoria → sugestões aparecem
- [ ] Clique em sugestão → redireciona corretamente

### 2. **Fluxo de Booking**
- [ ] Selecionar categoria → ir para etapa 1
- [ ] Preencher descrição → avançar
- [ ] Selecionar província → cidades aparecem automaticamente
- [ ] Selecionar cidade (Luanda) → bairros aparecem
- [ ] Escolher profissional → ver detalhes
- [ ] Preencher dados → confirmar reserva
- [ ] Ver página de sucesso

### 3. **Perfil de Profissional**
- [ ] Acessar perfil via URL: `/accounts/profissional/1/`
- [ ] Ver foto/nome/avaliação
- [ ] Ver serviços oferecidos
- [ ] Ver portfólio (se houver)
- [ ] Ver reviews (se houver)
- [ ] Ver áreas de atuação
- [ ] Botão "Ver Perfil" nos cards de profissionais

### 4. **Registro de Profissional**
- [ ] Acessar `/accounts/registro-profissional/`
- [ ] Etapa 1: Preencher nome, telefone, email
- [ ] Etapa 2: Preencher NIF, IBAN, bio
- [ ] Etapa 3: Selecionar serviços e áreas
- [ ] Etapa 4: Adicionar portfólio (ou pular)
- [ ] Ver mensagem de sucesso
- [ ] Verificar no admin (deve estar pendente)

### 5. **Sistema de Reviews**
- [ ] Criar reserva e marcar como "completed" no admin
- [ ] Acessar `/reviews/booking/1/` (substituir 1 pelo ID)
- [ ] Preencher avaliação (estrelas + comentário)
- [ ] Ver review aparecer no perfil do profissional
- [ ] Verificar que média foi atualizada

### 6. **Admin Panel**
- [ ] Login: `/admin/` (admin/admin123)
- [ ] Ver todos os modelos
- [ ] Ativar profissional pendente
- [ ] Ver reservas
- [ ] Moderar reviews
- [ ] Filtrar e buscar

---

## 🎯 **Cenários de Teste Recomendados**

### Cenário 1: Cliente faz reserva completa
1. Homepage → Clica em "Limpeza"
2. Vê sugestões → Clica em "Limpeza Residencial"
3. Descreve tarefa: "Preciso de limpeza completa do apartamento"
4. Seleciona: Luanda → Luanda → Talatona
5. Escolhe profissional (Maria Santos)
6. Preenche: nome, telefone, data, hora
7. Confirma → Vê sucesso

### Cenário 2: Profissional se cadastra
1. Clica "Cadastrar-se como Profissional"
2. Preenche 4 etapas
3. Recebe mensagem de sucesso
4. Admin ativa no painel
5. Profissional aparece em busca

### Cenário 3: Review após serviço
1. Admin marca reserva como "completed"
2. Cliente acessa página de review
3. Dá 5 estrelas e comenta
4. Review aparece no perfil
5. Média do profissional atualiza

---

## 📊 **Dados de Teste Disponíveis**

**Profissionais:**
- Maria Santos (Limpeza) - +244912345678
- João Silva (Montagem) - +244923456789
- Carlos Mendes (Canalização) - +244934567890
- Ana Costa (Elétrico) - +244945678901
- Pedro Alves (Mudanças) - +244956789012

**Credenciais Admin:**
- Username: `admin`
- Password: `admin123`

---

**Bom teste! 🚀**

