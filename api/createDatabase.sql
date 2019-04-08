BEGIN TRANSACTION;
CREATE TABLE `url_responses` ( `url_id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `request_id` INTEGER, `image_url` TEXT, `score` REAL, `marque` TEXT );
CREATE TABLE "images_request" ( `id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `request_date` TEXT, `client` TEXT, `base64` TEXT );
COMMIT;
