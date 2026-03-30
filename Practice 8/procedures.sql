CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_name VARCHAR(100),
    p_phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM phonebook WHERE name = p_name
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    invalid_data TEXT := '';
BEGIN
    IF array_length(p_names, 1) IS NULL OR array_length(p_phones, 1) IS NULL THEN
        RAISE NOTICE 'Empty arrays';
        RETURN;
    END IF;

    IF array_length(p_names, 1) <> array_length(p_phones, 1) THEN
        RAISE NOTICE 'Names and phones arrays must have the same length';
        RETURN;
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9]{11}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_names[i]) THEN
                UPDATE phonebook
                SET phone = p_phones[i]
                WHERE name = p_names[i];
            ELSE
                INSERT INTO phonebook(name, phone)
                VALUES (p_names[i], p_phones[i]);
            END IF;
        ELSE
            invalid_data := invalid_data || '(' || p_names[i] || ', ' || p_phones[i] || ') ';
        END IF;
    END LOOP;

    IF invalid_data <> '' THEN
        RAISE NOTICE 'Incorrect data: %', invalid_data;
    ELSE
        RAISE NOTICE 'All users inserted successfully';
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_user(value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = value OR phone = value;
END;
$$;