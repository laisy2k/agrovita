# Usuários e permissões do banco AgroVita

## Objetivo

Aplicar o princípio do menor privilégio, separando o usuário administrativo do banco do usuário utilizado pela aplicação Flask.

## Usuários configurados

### agrovita_admin

- Host: `localhost`
- Escopo: banco `agrovita`
- Permissões: todos os privilégios sobre `agrovita.*`
- Finalidade: administração das tabelas e dos objetos do banco.

### agrovita_app

- Host: `localhost`
- Escopo: banco `agrovita`
- Permissões: `SELECT`, `INSERT`, `UPDATE` e `DELETE`
- Finalidade: operações de leitura e manutenção de registros realizadas pela aplicação.

## Verificação

As permissões foram verificadas com os comandos:

```sql
SHOW GRANTS FOR 'agrovita_admin'@'localhost';
SHOW GRANTS FOR 'agrovita_app'@'localhost';
```

Os resultados confirmaram que o usuário administrativo possui privilégios limitados ao banco `agrovita`, enquanto o usuário da aplicação possui apenas as permissões de leitura, inserção, atualização e exclusão.

## Segurança

- Não armazenar senhas no repositório.
- Manter credenciais no arquivo `.env`, excluído do Git.
- Não utilizar o usuário `root` na aplicação.
- Conceder novas permissões somente quando forem necessárias.