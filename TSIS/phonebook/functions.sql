CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$;


CREATE OR REPLACE FUNCTION get_phonebook_page(lim INT, off INT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT lim OFFSET off;
END;
$$;