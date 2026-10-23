
-- =========================================================
-- AgroVita - Banco de Dados II
-- Issue #53: Procedures, Function e Trigger
-- SGBD: MySQL 8.0+
-- =========================================================

USE agrovita;

-- ---------------------------------------------------------
-- 1. PROCEDURE: consultar o historico de vacinacoes de
--    um animal, da mais recente para a mais antiga.
-- ---------------------------------------------------------

DROP PROCEDURE IF EXISTS sp_historico_vacinacoes;

DELIMITER $$

CREATE PROCEDURE sp_historico_vacinacoes(
    IN p_animal_id BIGINT
)
READS SQL DATA
BEGIN
    SELECT
        id,
        animal_id,
        vacina,
        lote,
        fabricante,
        data_aplicacao,
        proxima_dose,
        dose,
        responsavel,
        observacoes
    FROM vacinacoes
    WHERE animal_id = p_animal_id
    ORDER BY data_aplicacao DESC, id DESC;
END$$

DELIMITER ;

-- ---------------------------------------------------------
-- 2. FUNCTION: retornar a quantidade de vacinacoes
--    registradas para determinado animal.
-- ---------------------------------------------------------

DROP FUNCTION IF EXISTS fn_total_vacinacoes_animal;

DELIMITER $$

CREATE FUNCTION fn_total_vacinacoes_animal(
    p_animal_id BIGINT
)
RETURNS BIGINT
READS SQL DATA
BEGIN
    DECLARE v_total BIGINT DEFAULT 0;

    SELECT COUNT(*)
    INTO v_total
    FROM vacinacoes
    WHERE animal_id = p_animal_id;

    RETURN v_total;
END$$

DELIMITER ;

-- ---------------------------------------------------------
-- 3. TRIGGER: impedir que a proxima dose seja anterior
--    a data de aplicacao da vacina.
-- ---------------------------------------------------------

DROP TRIGGER IF EXISTS trg_validar_datas_vacinacao_insert;
DROP TRIGGER IF EXISTS trg_validar_datas_vacinacao_update;

DELIMITER $$

CREATE TRIGGER trg_validar_datas_vacinacao_insert
BEFORE INSERT ON vacinacoes
FOR EACH ROW
BEGIN
    IF NEW.proxima_dose IS NOT NULL
        AND NEW.proxima_dose < NEW.data_aplicacao THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'A proxima dose nao pode ser anterior a data de aplicacao.';
    END IF;
END$$

CREATE TRIGGER trg_validar_datas_vacinacao_update
BEFORE UPDATE ON vacinacoes
FOR EACH ROW
BEGIN
    IF NEW.proxima_dose IS NOT NULL
        AND NEW.proxima_dose < NEW.data_aplicacao THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'A proxima dose nao pode ser anterior a data de aplicacao.';
    END IF;
END$$

DELIMITER ;
