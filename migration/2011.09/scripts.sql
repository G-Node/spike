ALTER TABLE  `datafiles_datafile` ADD  `extracted_info` LONGTEXT CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL ;

ALTER TABLE  `datafiles_datafile` ADD  `convertible` TINYINT NULL ;

ALTER TABLE  `datafiles_datafile` ADD  `last_task_id` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL ;

ALTER TABLE  `datafiles_datafile` ADD  `extracted` VARCHAR( 20 ) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL ;
