# Documentação de Segurança — AgroVita

## 1. Introdução

O AgroVita é um sistema web desenvolvido em Python, utilizando Flask e SQLite, para o gerenciamento de animais, manejos sanitários e vacinações.

Foram implementados três conjuntos de mecanismos de segurança para proteger o acesso ao sistema, controlar sessões e registrar atividades dos usuários.

## 2. Mecanismos implementados

### 2.1. Autenticação e controle de acesso

O sistema utiliza autenticação por login e senha, com armazenamento das senhas em formato de hash.

As permissões são diferenciadas entre administradores e usuários comuns. As rotas protegidas exigem autenticação, enquanto as funcionalidades administrativas exigem a permissão correspondente.

As operações com animais, manejos e vacinações também utilizam verificações de propriedade dos registros, impedindo que usuários acessem ou modifiquem dados pertencentes a outras contas por essas operações.

**Testes realizados:**
- Login com credenciais válidas: aprovado.
- Tentativa de login com senha incorreta: aprovado.
- Acesso a rota protegida sem autenticação: aprovado.
- Tentativa de acesso administrativo com conta comum: aprovado.
- Isolamento dos registros entre usuários: aprovado.

**Resultado:** os cinco testes foram concluídos com sucesso.

### 2.2. Gerenciamento seguro de sessões

O sistema utiliza sessões do Flask para manter o usuário autenticado durante a navegação.

Foram implementados mecanismos de encerramento da sessão no logout, expiração após 30 minutos de inatividade, renovação do estado da sessão após autenticação e configurações de proteção dos cookies, incluindo `HttpOnly` e `SameSite=Lax`.

**Testes realizados:**
- Encerramento da sessão no logout: aprovado.
- Expiração por inatividade: aprovado.
- Verificação das configurações de proteção dos cookies: aprovado.
- Limpeza da sessão anterior durante o login: aprovado.

**Resultado:** os quatro testes foram concluídos com sucesso.

### 2.3. Logs de auditoria

Foi criada a tabela `logs_auditoria` no banco de dados SQLite para armazenar informações sobre ações realizadas no sistema.

Os registros incluem o identificador do usuário, o tipo da ação, detalhes do evento e a data e hora.

**Eventos registrados:**
- Login e logout.
- Cadastro, edição e exclusão de animais.
- Cadastro, edição e exclusão de manejos sanitários.
- Cadastro, edição e exclusão de vacinações.
- Tentativas de acesso administrativo não autorizado.
- Expiração de sessões por inatividade.

As operações de criação, edição e exclusão registram seus respectivos logs na mesma transação do banco de dados.

Os horários são armazenados em UTC, permitindo sua conversão para o fuso horário local durante a apresentação.

**Testes realizados:**
- Registros de login e logout: aprovado.
- Registros do CRUD de animais: aprovado.
- Registros do CRUD de manejos: aprovado.
- Registros do CRUD de vacinações: aprovado.
- Registros de eventos de segurança: aprovado.
- Verificação dos dados armazenados nos logs: aprovado.

**Resultado:** os seis testes foram concluídos com sucesso.

## 3. Resumo da validação

| Mecanismo | Testes aprovados |
|---|---|
| Autenticação e controle de acesso | 5 de 5 |
| Gerenciamento de sessões | 4 de 4 |
| Logs de auditoria | 6 de 6 |
| **Total** | **15 de 15** |

Os testes funcionais realizados não apresentaram falhas nos cenários avaliados. Esses resultados não substituem uma auditoria de segurança completa.

## 4. Tecnologias utilizadas

- Python
- Flask
- SQLite
- Werkzeug para geração e verificação de hashes de senhas
- Sessões e cookies HTTP
- Consultas SQL parametrizadas

## 5. Evidências

As evidências dos testes podem incluir capturas de tela das páginas de login, mensagens de acesso negado, expiração de sessão e consultas aos logs de auditoria.

As capturas devem ocultar senhas, chaves secretas e informações pessoais desnecessárias.

## 6. Conclusão

A implementação dos mecanismos de autenticação, controle de acesso, gerenciamento de sessões e logs de auditoria contribuiu para melhorar a proteção do AgroVita.

Os 15 testes realizados foram aprovados, demonstrando o funcionamento dos mecanismos nos cenários avaliados e atendendo à etapa de implementação e validação dos mecanismos de segurança previstos para o projeto.