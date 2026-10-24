# Restauração e validação do banco de dados AgroVita

## 1. Objetivo

Documentar o procedimento de restauração do banco de dados AgroVita e registrar os testes realizados para verificar a integridade dos dados, tabelas, procedures, functions e triggers.

## 2. Arquivo de backup

O arquivo `docs/dump_agrovita.sql` contém a estrutura do banco de dados AgroVita, incluindo tabelas, procedures e triggers, sem os registros armazenados. Essa versão é destinada à publicação no repositório sem expor dados de usuários.

Para a validação da restauração, foi utilizado separadamente um dump completo, armazenado temporariamente fora do repositório. Esse arquivo incluiu os dados necessários para comparar as quantidades de registros e testar o funcionamento das rotinas restauradas.

O backup completo não deve ser publicado sem uma revisão dos dados e a autorização adequada.


## 3. Procedimento de restauração

O arquivo `docs/dump_agrovita.sql` contém a estrutura do banco, incluindo tabelas, procedures, functions e triggers, mas não contém os registros armazenados.

Para restaurar essa estrutura, com o MySQL em execução, utilize:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p < docs\dump_agrovita.sql
```

O comando solicita a senha do usuário MySQL informado. Como o arquivo foi gerado com `--databases agrovita`, ele contém instruções para selecionar o banco `agrovita`.

**Atenção:** o dump contém comandos que podem remover e recriar tabelas existentes. Execute o procedimento somente em um ambiente apropriado, preferencialmente um banco de teste vazio. Não o execute diretamente em um banco com dados importantes sem um backup completo e uma avaliação prévia dos impactos.

A restauração da estrutura não recupera os registros originais. Para recuperar dados, é necessário um backup completo validado e protegido contra divulgação indevida.


## 4. Teste de restauração

Para validar o backup sem utilizar o banco original, foi criado um banco separado chamado `agrovita_teste_restauracao`.

Foi gerado um dump temporário sem a opção `--databases`, permitindo importar seu conteúdo no banco de teste sem selecionar o banco original.

A importação foi executada pelo cliente MySQL com o comando `SOURCE`, utilizando o arquivo temporário.

## 5. Resultados da validação

Após a restauração, foram confirmadas as seguintes quantidades:

| Tabela | Registros |
|---|---:|
| usuarios | 3 |
| animais | 3 |
| vacinacoes | 2 |
| manejos | 0 |
| logs_auditoria | 61 |

Também foram confirmadas a presença da procedure `sp_historico_vacinacoes`, da função `fn_total_vacinacoes_animal` e dos triggers `trg_validar_datas_vacinacao_insert` e `trg_validar_datas_vacinacao_update`.

### Testes funcionais

- A procedure `sp_historico_vacinacoes(10)` retornou as duas vacinações do animal 10.
- A função `fn_total_vacinacoes_animal(10)` retornou `2`.
- Uma tentativa de definir a próxima dose antes da data de aplicação foi bloqueada pelo trigger.
- A consulta posterior confirmou que o registro permaneceu com os valores originais: aplicação em `2026-10-08` e próxima dose em `2026-10-12`.

## Validação do dump público

O dump público `docs/dump_agrovita.sql` foi restaurado em um banco separado, denominado `agrovita_teste_dump_publico`, para evitar alterações no banco original.

Após a importação, foram confirmados:

- As cinco tabelas do banco de dados.
- A procedure `sp_historico_vacinacoes`.
- A função `fn_total_vacinacoes_animal`.
- Os triggers `trg_validar_datas_vacinacao_insert` e `trg_validar_datas_vacinacao_update`.

O arquivo foi validado quanto à restauração da estrutura e das rotinas. Como se trata de um dump sem registros, essa validação não comprova a recuperação de dados.

A restauração foi executada com o usuário MySQL `root`, que passou a constar como definidor das rotinas criadas durante o teste.


## 6. Conclusão

O teste confirmou a restauração das cinco tabelas, dos dados existentes, da procedure, da função e dos dois triggers. Os testes funcionais também confirmaram o comportamento esperado das rotinas e a rejeição de uma data de vacinação inválida.

A validação foi realizada em um banco separado, preservando o banco original durante os testes.
