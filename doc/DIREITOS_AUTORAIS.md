# 🛡️ Proteção de Direitos Autorais

## ⚠️ Problema Identificado

O projeto estava usando **imagens externas do TaskRabbit** (domínio `ctfassets.net`) nos fixtures, o que poderia causar problemas de direitos autorais.

## ✅ Solução Implementada

### 1. **Ícones SVG Próprios**
Criados ícones SVG originais e sem direitos autorais em:
- `static/images/icons/cleaning.svg` - Limpeza
- `static/images/icons/furniture.svg` - Montagem de Móveis
- `static/images/icons/wall-mount.svg` - Montagem em Parede
- `static/images/icons/plumbing.svg` - Canalização
- `static/images/icons/electrical.svg` - Elétrico
- `static/images/icons/moving.svg` - Mudanças

### 2. **Modelo Atualizado**
O modelo `ServiceCategory` agora:
- Permite `icon_url` ser opcional (null/blank)
- Tem método `get_icon_url()` que usa ícone SVG local se `icon_url` não estiver definido
- Mantém suporte para URLs externas se necessário (mas recomendamos usar ícones locais)

### 3. **Fixtures Atualizados**
- Removidas todas as URLs externas do TaskRabbit
- Ícones agora são carregados automaticamente dos SVGs locais

## 📋 Checklist de Conformidade

### ✅ Resolvido
- [x] Imagens de categorias de serviço substituídas por SVGs próprios
- [x] URLs externas removidas dos fixtures
- [x] Templates atualizados para usar `get_icon_url()`
- [x] Admin atualizado para exibir ícones corretamente

### ⚠️ Atenção Necessária

#### 1. **Imagens de Portfólio dos Profissionais**
As imagens em `media/professionals/portfolio/` são **uploadadas pelos usuários**. Você precisa:

- **Termos de Uso**: Adicionar cláusula no registro que:
  - Usuário declara ter direitos sobre as imagens
  - Concede licença para uso na plataforma
  - Responsabiliza usuário por violações de direitos autorais

**Exemplo de cláusula:**
```
"Declaro que possuo todos os direitos autorais sobre as imagens 
enviadas e concedo à plataforma licença para uso, exibição e 
reprodução dessas imagens no contexto dos serviços oferecidos. 
Assumo total responsabilidade por qualquer violação de direitos 
autorais."
```

#### 2. **Imagens de Perfil**
- Fotos de perfil também são uploads de usuários
- Mesma proteção necessária (Termos de Uso)

#### 3. **Fontes e Bibliotecas CSS/JS**
- **Tailwind CSS**: ✅ Open Source (MIT License) - OK
- Verifique outras bibliotecas frontend se adicionadas

## 🎨 Como Adicionar Novos Ícones

1. Crie um SVG em `static/images/icons/[nome].svg`
2. Atualize o mapeamento em `ServiceCategory.get_icon_url()`:
```python
icon_map = {
    'seu-slug': 'images/icons/seu-icone.svg',
    # ...
}
```

## 📝 Recomendações Adicionais

### 1. **Termos de Serviço**
Criar documento legal que inclua:
- Política de direitos autorais
- Responsabilidade do usuário sobre conteúdo enviado
- Política de remoção (DMCA)

### 2. **Moderação de Conteúdo**
- Sistema de denúncia para imagens suspeitas
- Capacidade de remover conteúdo reportado

### 3. **Imagens Gratuitas**
Se precisar de fotos adicionais, use serviços com licença livre:
- **Unsplash** (Unsplash License - livre para uso comercial)
- **Pexels** (Licença livre)
- **Pixabay** (Pixabay License - livre)
- **Flaticon** (com atribuição ou plano pago)

### 4. **Verificação Legal**
Antes de ir para produção:
- [ ] Revisar Termos de Uso com advogado
- [ ] Adicionar política de privacidade
- [ ] Implementar sistema de denúncia
- [ ] Configurar processo de remoção de conteúdo

## 🔍 Verificação Contínua

Após cada deploy, verifique:
- Nenhuma URL externa de imagem não autorizada
- Todos os ícones são locais ou de fontes verificadas
- Termos de Uso atualizados e visíveis

---

**Última atualização**: Novembro 2024
**Status**: ✅ Ícones de categorias protegidos
**Próximos passos**: Implementar Termos de Uso e moderação

