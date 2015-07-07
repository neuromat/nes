
load-icd-table directory: how to load icd (International classification of diseases) table to NES.

1- Unzip CID10CSV.zip. It contains the international classification of diseases provided by Brazilian government (http://www.datasus.gov.br/cid10/V2008/cid10.htm).
2- Copy CID-10-CATEGORIAS.CSV and CID-10-SUBCATEGORIAS.CSV to /tmp directory.
3- Run the postgres script inside the file cid10_etl.txt in NES database. (psql -d <nes-database-name> -a -f cid10_etl.txt)

