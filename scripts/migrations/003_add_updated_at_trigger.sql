CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_store_updated_at
BEFORE UPDATE ON store
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
