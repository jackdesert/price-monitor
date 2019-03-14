-- tire_ids to keep
SELECT distinct(tire_id) FROM simpletire_reading WHERE in_stock = 't'

-- tire_ids to drop
SELECT id FROM simpletire_tire WHERE id NOT IN (
    SELECT distinct(tire_id) FROM simpletire_reading WHERE in_stock = 't'
  )


-- drop readings
DELETE FROM simpletire_reading WHERE tire_id IN(
    -- tire_ids to drop
    SELECT id FROM simpletire_tire WHERE id NOT IN (
        SELECT distinct(tire_id) FROM simpletire_reading WHERE in_stock = 't'
      )
  );

-- drop tires
DELETE FROM simpletire_tire WHERE id IN(
    -- tire_ids to drop
    SELECT id FROM simpletire_tire WHERE id NOT IN (
        SELECT distinct(tire_id) FROM simpletire_reading WHERE in_stock = 't'
      )
  );


