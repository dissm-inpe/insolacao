# insolacao
Código para o cáculo da insolação diária baseado em Ceballos et al., 2008. 


Input: Refletância VIS GOES (S11167029_YYYYMMDDHHMM.ref)


Output: S11167051_YYYYMMDD0000.bin/ S11167051_YYYYMMDD0000.nc


| Etapa     | Input                       | Processamento                             | Output                     |
| --------- | --------------------------- | ----------------------------------------- | -------------------------- |
| Diário    | Refletância VIS GOES (7029) | Fração de céu limpo + integração temporal | Insolação diária (7051)    |
| Quinzenal | Insolação diária (7051)     | Média 15 dias                             | Insolação quinzenal (7053) |
| Mensal    | Insolação diária (7051)     | Média mensal                              | Insolação mensal (7055)    |
| Conversão | BIN (7051/7053/7055)        | GMT + GDAL                                | NC (7067/7068/7069)        |
