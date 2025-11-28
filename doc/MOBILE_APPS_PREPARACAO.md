# 📱 Preparação para Apps Móveis (Android & iOS)

## ✅ Por que está preparado

O projeto já tem um sistema de notificações centralizado que facilita muito a criação de apps móveis. Todas as notificações estão em `core/emails.py`, o que significa que podemos facilmente adicionar notificações push sem duplicar lógica.

## 📋 Notificações Existentes (Já Funcionam)

### 1. **Confirmação de Reserva para Cliente**
```python
send_booking_confirmation_to_client(booking)
```
- Envia email quando cliente faz uma reserva
- **Para móvel**: Enviar push notification + email

### 2. **Notificação de Nova Reserva para Profissional**
```python
send_booking_notification_to_professional(booking)
```
- Avisa profissional sobre nova reserva
- **Para móvel**: Push notification prioritária!

### 3. **Atualização de Status de Reserva**
```python
send_booking_status_update_to_client(booking, old_status)
```
- Notifica cliente quando status muda (confirmado, iniciado, concluído)
- **Para móvel**: Push notification essencial

### 4. **Notificação de Registro de Profissional**
```python
send_professional_registration_notification(professional)
```
- Avisa admin sobre novo cadastro
- **Para móvel**: Push para admin (se tiver app)

### 5. **Email de Ativação de Profissional**
```python
send_professional_activation_email(professional)
```
- Confirma ativação da conta
- **Para móvel**: Push notification de boas-vindas

## 🚀 Como Adaptar para Apps Móveis

### Opção 1: Criar Camada de Notificações Unificada (Recomendado)

Criar um módulo `core/notifications.py` que envia tanto email quanto push:

```python
# core/notifications.py (futuro)
from core.emails import (
    send_booking_confirmation_to_client as send_email_confirmation,
    send_booking_notification_to_professional as send_email_notification,
    # ... outras funções
)

def send_booking_confirmation_to_client(booking, send_email=True, send_push=True):
    """Envia confirmação por email e/ou push"""
    if send_email:
        send_email_confirmation(booking)
    
    if send_push:
        # Enviar push notification para app móvel
        send_push_notification(
            user=booking.client,
            title="Reserva Confirmada",
            body=f"Sua reserva de {booking.service.category.name} foi confirmada!",
            data={'type': 'booking_confirmed', 'booking_id': booking.id}
        )
```

### Opção 2: Adicionar Push Notifications às Funções Existentes

Modificar `core/emails.py` para também enviar push:

```python
def send_booking_notification_to_professional(booking):
    """Send new booking notification - Email + Push"""
    
    # Email (já existe)
    send_email(...)
    
    # Push Notification (adicionar)
    if booking.professional.fcm_token:  # Token do Firebase/APNs
        send_push_notification(
            token=booking.professional.fcm_token,
            title="Nova Reserva Recebida!",
            body=f"Você recebeu uma nova reserva de {booking.client.name}",
            data={'booking_id': booking.id}
        )
```

## 🔧 Tecnologias para Push Notifications

### Android
- **Firebase Cloud Messaging (FCM)** - Grátis, fácil de integrar
- Biblioteca Python: `pyfcm` ou `firebase-admin`

### iOS
- **Apple Push Notification Service (APNs)** - Necessário certificado Apple Developer
- Biblioteca Python: `pyapns2` ou `PyAPNs2`

### Solução Unificada
- **Firebase Cloud Messaging** - Funciona para Android E iOS
- Uma única API para ambos

## 📱 Modelos de Dados Necessários (Adicionar)

```python
# accounts/models.py (adicionar campos)

class Client(models.Model):
    # ... campos existentes ...
    fcm_token = models.CharField(max_length=255, blank=True, null=True)  # Token do Firebase
    push_notifications_enabled = models.BooleanField(default=True)

class Professional(models.Model):
    # ... campos existentes ...
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    push_notifications_enabled = models.BooleanField(default=True)
```

## 🔌 APIs Necessárias para Apps Móveis

### Autenticação
- `/api/auth/login/` - Login com telefone
- `/api/auth/verify/` - Verificação de código (WhatsApp/SMS)
- `/api/auth/logout/` - Logout
- `/api/auth/register-fcm/` - Registrar token FCM

### Reservas (Bookings)
- `GET /api/bookings/` - Listar reservas do usuário
- `POST /api/bookings/` - Criar nova reserva
- `GET /api/bookings/{id}/` - Detalhes da reserva
- `PATCH /api/bookings/{id}/status/` - Atualizar status (profissional)

### Profissionais
- `GET /api/professionals/` - Buscar profissionais (com filtros)
- `GET /api/professionals/{id}/` - Perfil do profissional
- `POST /api/professionals/` - Registrar como profissional

### Serviços e Categorias
- `GET /api/categories/` - Listar categorias
- `GET /api/categories/{slug}/professionals/` - Profissionais por categoria

### Localização
- `GET /api/provinces/` - Listar províncias
- `GET /api/cities/{province_id}/` - Cidades por província
- `GET /api/neighborhoods/{city_id}/` - Bairros por cidade

### Reviews
- `GET /api/bookings/{id}/review/` - Ver review
- `POST /api/bookings/{id}/review/` - Criar review

## 🛠️ Implementação Recomendada

### Passo 1: Criar API REST com Django REST Framework
```bash
pip install djangorestframework
```

### Passo 2: Adicionar FCM Token aos Models
```python
# Migration para adicionar fcm_token
```

### Passo 3: Criar Serviço de Push Notifications
```python
# core/push_notifications.py
from pyfcm import FCMNotification

def send_push_notification(user, title, body, data=None):
    if not user.fcm_token:
        return False
    
    push_service = FCMNotification(api_key=settings.FCM_API_KEY)
    result = push_service.notify_single_device(
        registration_id=user.fcm_token,
        message_title=title,
        message_body=body,
        data_message=data
    )
    return result
```

### Passo 4: Integrar Push nas Notificações Existentes
Modificar funções em `core/emails.py` para também enviar push.

## 📦 Dependências Futuras

```txt
# requirements.txt (adicionar para apps móveis)
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0  # Autenticação JWT
pyfcm>=1.5.0  # Firebase Cloud Messaging
```

## ✅ Vantagens da Arquitetura Atual

1. **Notificações Centralizadas**: Tudo em `core/emails.py` - fácil adicionar push
2. **Modelos Prontos**: Client e Professional já existem - só adicionar FCM token
3. **Lógica de Negócio Separada**: Views podem virar API views facilmente
4. **Autenticação por Telefone**: Já funciona - perfeito para apps móveis angolanos

## 🎯 Próximos Passos (Quando Quiser Criar Apps)

1. ✅ Instalar Django REST Framework
2. ✅ Criar serializers para todos os models
3. ✅ Criar API views (reutilizar lógica das views atuais)
4. ✅ Adicionar FCM tokens aos models
5. ✅ Integrar push notifications
6. ✅ Testar com apps nativos (React Native, Flutter, ou nativo)

## 📝 Notas Importantes

- **WhatsApp Business API**: No futuro, pode integrar para verificação via WhatsApp (mais comum em Angola)
- **SMS Gateway**: Alternativa para verificação (ex: Twilio, AWS SNS)
- **Offline Support**: Apps móveis podem trabalhar offline e sincronizar depois

---

**Conclusão**: Sim, está bem preparado! O sistema de notificações atual pode ser facilmente estendido para push notifications, e a arquitetura Django facilita criar APIs REST para os apps móveis.

