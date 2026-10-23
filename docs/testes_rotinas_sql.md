# AgroVita — Testes das rotinas SQL

## 1. Procedure `sp_historico_vacinacoes`

**Objetivo:** consultar o histórico de vacinações de um animal, ordenado da mais recente para a mais antiga.

**Comando executado:**

```sql
CALL sp_historico_vacinacoes(10);
```

**Resultado:** sucesso. A consulta retornou duas vacinações do animal de ID 10.

## 2. Function `fn_total_vacinacoes_animal`

**Objetivo:** contar as vacinações registradas para um animal.

**Comando executado:**

```sql
SELECT fn_total_vacinacoes_animal(10) AS total_vacinacoes;
```

**Resultado esperado e obtido:** `2`.

O animal de ID 9, sem vacinações registradas, retornou `0`.

## 3. Trigger de INSERT

**Objetivo:** impedir que a próxima dose seja anterior à data de aplicação.

**Teste executado:** tentativa de inserir uma vacinação com aplicação em `2026-10-20` e próxima dose em `2026-10-19`.

**Resultado:** rejeitado com erro `1644 (45000)`, conforme esperado.

## 4. Trigger de UPDATE

**Objetivo:** aplicar a mesma validação durante atualizações.

**Teste válido:** alteração temporária da próxima dose do registro de ID 5 para `2026-10-13`.

**Resultado:** atualização executada com sucesso. A transação foi revertida com `ROLLBACK`.

**Teste inválido:** tentativa de definir a próxima dose como `2026-10-07`, anterior à aplicação em `2026-10-08`.

**Resultado:** rejeitado com erro `1644 (45000)`.

## 5. Integridade dos dados

Após os testes, o registro de ID 5 permaneceu com a data de aplicação `2026-10-08` e a próxima dose `2026-10-12`.

## 6. Rotinas implementadas

- Procedure: `sp_historico_vacinacoes`.
- Function: `fn_total_vacinacoes_animal`.
- Trigger: `trg_validar_datas_vacinacao_insert`.
- Trigger: `trg_validar_datas_vacinacao_update`.

Os testes foram realizados no banco MySQL `agrovita`.