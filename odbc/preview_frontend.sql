-- This is the script to create a direct DB-based "read" front-end for the end-users

-- my experiments
CREATE VIEW odbc_my_experiments AS 
SELECT title, caption, date_created, username AS owner, exp_type, subject
FROM experiments_experiment INNER JOIN auth_user ON experiments_experiment.owner_id = auth_user.id
WHERE auth_user.username = (SELECT SUBSTRING_INDEX((SELECT USER()),'@',1))

-- shared experiments
CREATE VIEW odbc_shared_experiments AS
SELECT title, caption, date_created, username AS owner, exp_type, subject
FROM experiments_experiment RIGHT OUTER JOIN state_machine_safetylevel_shared_with ON experiments_experiment.safetylevel_ptr_id = state_machine_safetylevel_shared_with.safetylevel_id RIGHT OUTER JOIN auth_user ON state_machine_safetylevel_shared_with.user_id = auth_user.id
WHERE auth_user.username = (SELECT SUBSTRING_INDEX((SELECT USER()),'@',1))

-- my datasets
CREATE VIEW odbc_my_datasets AS 
SELECT title, caption, date_added, username AS owner, dataset_qty, tags
FROM datasets_rdataset INNER JOIN auth_user ON datasets_rdataset.owner_id = auth_user.id
WHERE auth_user.username = (SELECT SUBSTRING_INDEX((SELECT USER()),'@',1))

-- shared experiments
CREATE VIEW odbc_shared_datasets AS
SELECT title, caption, date_added, username AS owner, dataset_qty, tags
FROM datasets_rdataset INNER JOIN state_machine_safetylevel_shared_with ON datasets_rdataset.safetylevel_ptr_id = state_machine_safetylevel_shared_with.safetylevel_id RIGHT OUTER JOIN auth_user ON state_machine_safetylevel_shared_with.user_id = auth_user.id
WHERE auth_user.username = (SELECT SUBSTRING_INDEX((SELECT USER()),'@',1))
