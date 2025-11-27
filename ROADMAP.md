# Roadmap de Desenvolvimento - Conheces Alguém?

## ✅ Concluído
- [x] Estrutura Django completa
- [x] Modelos (Client, Professional, Booking, Review, Services, Locations)
- [x] Django Admin configurado
- [x] Homepage moderna e responsiva
- [x] Database com dados iniciais (18 províncias, categorias)

---

## 🚀 Próximas Funcionalidades (Prioridade)

### **Fase 1: Fluxo de Reserva (BOOKING)** ⭐ PRIORIDADE MÁXIMA

#### 1.1 Views e URLs para Serviços
- [ ] Listar categorias de serviços
- [ ] Página de detalhes da categoria
- [ ] Listar profissionais por categoria e localização

#### 1.2 Fluxo de Booking em 3 Etapas
- [ ] **Etapa 1: Seleção de Serviço**
  - Selecionar categoria
  - Descrever a tarefa
  - Guardar na sessão
  
- [ ] **Etapa 2: Seleção de Localização**
  - Dropdown de província
  - Dropdown de cidade (filtrado por província)
  - Dropdown de bairro (apenas para Luanda)
  - Campo de endereço (opcional)
  - Guardar na sessão

- [ ] **Etapa 3: Seleção de Profissional e Confirmação**
  - Listar profissionais disponíveis (filtrado por localização e categoria)
  - Mostrar perfil resumido (foto, nome, avaliação, número de reviews)
  - Formulário de reserva (data, hora, instruções especiais)
  - Criar reserva no banco

#### 1.3 Autenticação Básica de Cliente
- [ ] Formulário simples de telefone e nome
- [ ] Criar ou buscar cliente existente
- [ ] Guardar cliente na sessão

---

### **Fase 2: Registro de Profissionais**

#### 2.1 Formulário de Registro
- [ ] Formulário multi-etapas
- [ ] Validação de campos
- [ ] Upload de fotos (perfil e portfólio)
- [ ] Seleção de categorias de serviços
- [ ] Seleção de áreas de atuação (províncias/cidades)

#### 2.2 Confirmação e Pendência
- [ ] Página de confirmação de registro
- [ ] Mensagem de aguardar ativação pelo admin
- [ ] Notificação para admin (email/log)

---

### **Fase 3: Perfis e Visualizações**

#### 3.1 Perfil de Profissional
- [ ] Página pública do profissional
- [ ] Informações: nome, foto, avaliação, bio
- [ ] Portfólio de trabalhos
- [ ] Lista de reviews
- [ ] Serviços oferecidos
- [ ] Áreas de atuação

#### 3.2 Dashboard de Profissional
- [ ] Ver reservas recebidas
- [ ] Aceitar/rejeitar reservas
- [ ] Atualizar status de reservas
- [ ] Ver estatísticas básicas

---

### **Fase 4: Sistema de Reviews**

#### 4.1 Criar Review
- [ ] Formulário de review após reserva concluída
- [ ] Sistema de rating (1-5 estrelas)
- [ ] Campo de comentário
- [ ] Atualização automática da média do profissional

#### 4.2 Exibir Reviews
- [ ] Lista de reviews no perfil
- [ ] Filtros (recentes, melhor avaliado, etc.)
- [ ] Moderação (admin pode aprovar/reprovar)

---

### **Fase 5: Melhorias e Polimento**

#### 5.1 Autenticação Melhorada
- [ ] Verificação por código WhatsApp (manual inicialmente)
- [ ] Sistema de sessão melhorado
- [ ] Recuperação de conta

#### 5.2 Busca e Filtros
- [ ] Busca por texto
- [ ] Filtros avançados (preço, avaliação, disponibilidade)
- [ ] Ordenação (melhor avaliado, mais próximo, etc.)

#### 5.3 Notificações
- [ ] Email de confirmação de reserva
- [ ] Notificações para profissionais (nova reserva)
- [ ] Lembretes de reservas

---

## 📝 Notas de Implementação

### Ordem Recomendada:
1. **Fluxo de Booking** (mais importante - usuário final precisa disso)
2. **Registro de Profissionais** (precisa ter profissionais no sistema)
3. **Perfis** (para mostrar profissionais)
4. **Reviews** (valor agregado)

### Decisões Técnicas:
- Usar **sessão Django** para guardar dados temporários do booking
- **Não requer login** para clientes fazerem reservas inicialmente
- Formulários usar **django-crispy-forms** com Bootstrap 5
- Validar telefone com **django-phonenumber-field**

---

**Status Atual**: Pronto para implementar Fase 1! 🚀

