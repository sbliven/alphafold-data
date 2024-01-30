## Databases

| Flag                     | Required    | Used by                   | Standard Path                                                | Download | Expand | Update             | URL                                                                                                                                                                                                              | Versioned Path                                               |
|--------------------------|-------------|---------------------------|--------------------------------------------------------------|----------|--------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| data_dir                 |             |                           |                                                              |          |        |                    |                                                                                                                                                                                                                  |                                                              |
| param                    |             | RunModel                  |                                                              | aria2c   | tar    | Alphafold releases | https://storage.googleapis.com/alphafold/alphafold_params_2021-10-27.tar                                                                                                                                         |                                                              |
| bfd_database_path        | full_dbs    | DataPipeline              | bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt | aria2c   | tar    | Never?             | https://storage.googleapis.com/alphafold-databases/casp14_versions/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz                                                                               | bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt |
| mgnify_database_path     |             | DataPipeline              | mgnify/mgy_clusters_2018_12.fa                               | aria2c   | gunzip | Never?             | https://storage.googleapis.com/alphafold-databases/casp14_versions/mgy_clusters_2018_12.fa.gz                                                                                                                    | mgnify/mgy_clusters_2018_12.fa                               |
| template_mmcif_dir       |             | Hmm/HhsearchHitFeaturizer | pdb_mmcif/mmcif_files                                        | rsync    | custom | wwpdb              | rsync.rcsb.org::ftp_data/structures/divided/mmCIF/                                                                                                                                                               | pdb/mmcif_files                                              |
| obsolete_pdbs_path       |             | Hmm/HhsearchHitFeaturizer | pdb_mmcif/obsolete.dat                                       | aria2c   | none   | wwpdb              | ftp://ftp.wwpdb.org/pub/pdb/data/status/obsolete.dat                                                                                                                                                             | pdb/obsolete.dat                                             |
| pdb_seqres_database_path | multimer    | Hmmsearch                 | pdb_seqres/pdb_seqres.txt                                    | aria2c   | none   | wwpdb              | ftp://ftp.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt                                                                                                                                                          | pdb/pdb_seqres.txt                                           |
| pdb70_database_path      | monomer     | HHSearch                  | pdb70/pdb70                                                  | aria2c   | tar    | Never?             | http://wwwuser.gwdg.de/~compbiol/data/hhsuite/databases/hhsuite_dbs/old-releases/pdb70_from_mmcif_200401.tar.gz                                                                                                  | pdb70/pdb70                                                  |
| small_bfd_database_path  | reduced_dbs | DataPipeline              | small_bfd/bfd-first_non_concensus_sequences.fasta            | aria2c   | gunzip | Never?             | https://storage.googleapis.com/alphafold-databases/reduced_dbs/bfd-first_non_consensus_sequences.fasta.gz                                                                                                        | small_bfd/bfd-first_non_concensus_sequences.fasta            |
| uniclust30_database_path | full_dbs    | DataPipeline              | uniclust30/uniclust30_2018_08/uniclust30_2018_08             | aria2c   | tar    | Never?             | https://storage.googleapis.com/alphafold-databases/casp14_versions/uniclust30_2018_08_hhsuite.tar.gz                                                                                                             | uniclust30/uniclust30_2018_08/uniclust30_2018_08             |
| uniprot_database_path    | multimer    | DataPipeline              | uniprot/uniprot.fasta                                        | aria2c   | custom | uniprot            | ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_trembl.fasta.gz ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz | uniprot/uniprot.fasta                                        |
| uniref90_database_path   |             | DataPipeline              | uniref90/uniref90.fasta                                      | aria2c   | gunzip | uniprot            | ftp://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz                                                                                                                                    | uniprot/uniref90.fasta                                       |

## Processing outline

1. Features. `data_pipeline.process` fasta -> MSA, features.pkl
  1. For each chain:
    1. jackhmmer uniref90 -> uniref90_hits.sto
    2. jackhmmer mgnify -> mgnify_hits.sto
    3. `template_searcher.query` -> pdb_hits.hhr
    4. hhblits bfd -> bfd_uniclust_hits.a3m
      - or jackhmmer small_bfd -> small_bfd_hits.sto
    5. Deduplicate everything & convert into features
2. For each Model:
  1. *process_features* `model_runner.process_features` features -> processed_features
  2. *predict_and_compile* `model_runner.predict` processed_features -> JAX model
  3. *predict_benchmark* only if --benchmark (runs predict a second time to
      exclude compilation step)
  4. Output result*.pkl, unrelaxed.pdb
  5. *relax* `amber_relaxere.process` and write relaxed.pdb
3. Rank & write ranked.pdb

## File formats
- STO: stockholm MSA
- A3M: MSA

## Tools
- Hhsearch
  - Formats: a3m -> hhr
- Hmmsearch
  - Formats: sto -> (hmm) -> sto

Download command:
```
# http, ftp
aria2c src --dir=dst/
# rsync
rsync -rlptz --info=progress2 --delete --port=33444 rsync.rcsb.org::ftp_data/structures/divided/mmCIF/ pdb_mmcif/raw
```

Extract command:
```
# tar, tgz, tar.gz
tar xpvf SRC.tar --directory=DST
# .gz
pushd DST; gunzip SRC.gz; popd
```

## Directory Structure

- compressed
  - bfd/6a634dc6eb105c2e9b4cba7bbae93412/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz
  - mgnify/2018_12/mgy_clusters_2018_12.fa.gz
  - params/2021-10-27/alphafold_params_2021-10-27.tar
  - pdb/2021-12-02/
    - raw
    - obsolete.dat -> uncompressed
    - pdb_seqres.txt -> uncompressed
  - pdb70/200401/pdb70_from_mmcif_200401.tar.gz
  - uniclust30/2018_08/uniclust30_2018_08_hhsuite.tar.gz
  - uniprot/2021_04/
    - uniprot_trembl.fasta.gz
    - uniprot_sprot.fasta.gz
    - uniref90.fasta.gz
- uncompressed
  - Like above, except for:
  - pdb/2021-12-02
    - mmcif_files
    - obsolete.dat
    - pdb_seqres.txt
  - uniprot/2021_04/
    - uniporot.fasta
    - uniref90.fasta
- versions
  - latest -> 2021-12-02
  - 2021-12-02
    - bfd -> ../uncompressed/bfd/6a634dc6eb105c2e9b4cba7bbae93412
    - mgnify -> ../uncompressed/mgnify/2018_12
    - params -> ../uncompressed
    - pdb70/
    - pdb_mmcif/
      - mmcif_files/
      - obsolete.dat
    - pdb_seqres/
      - pdb_seqres.txt
    - small_bfd/
      - bfd-first_non_consensus_sequences.fasta
    - uniclust30/
      - uniclust30_2018_08/
    - uniprot/
      - uniprot.fasta
    - uniref90/
      - uniref90.fasta

In summary:
- `compressed` has the compressed files, split by version. It can be deleted without problems
- `uncompressed` has the uncompressed files, split by version. Old versions can be cleaned up when no longer linked
- `versions` is completely sym-links


[//]: # ( vim: set nowrap: )
