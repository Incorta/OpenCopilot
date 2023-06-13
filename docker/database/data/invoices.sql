-- Create temporary table
CREATE TEMPORARY TABLE temp_invoices (
    InvoiceNo TEXT,
    StockCode TEXT,
    Description TEXT,
    Quantity TEXT,
    InvoiceDate TEXT,
    UnitPrice TEXT,
    CustomerID TEXT,
    Country TEXT
);

-- Load CSV data into temporary table
COPY temp_invoices (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
FROM '/var/lib/mysql-files/invoices.csv' DELIMITER ',' CSV HEADER;

-- Create final table
CREATE TABLE invoices (
    InvoiceNo VARCHAR(20),
    StockCode VARCHAR(20),
    Description TEXT,
    Quantity INTEGER,
    InvoiceDate TIMESTAMP,
    UnitPrice FLOAT,
    CustomerID INTEGER,
    Country VARCHAR(100)
);

-- Populate final table with data from temporary table, transforming data as necessary
INSERT INTO invoices
SELECT
    InvoiceNo,
    StockCode,
    Description,
    CAST(Quantity AS INTEGER),
    TO_TIMESTAMP(InvoiceDate, 'MM/DD/YYYY HH24:MI') AS InvoiceDate,
    CAST(UnitPrice AS FLOAT),
    NULLIF(CustomerID, '')::INTEGER,
    Country
FROM temp_invoices;

-- Clean up
DROP TABLE temp_invoices;

