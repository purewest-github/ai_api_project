-- 既存のデータベースを削除
DROP DATABASE IF EXISTS AI_API_DB;
DROP DATABASE IF EXISTS test_AI_API_DB;

-- データベースを作成
CREATE DATABASE AI_API_DB;
CREATE DATABASE test_AI_API_DB;

-- ユーザーが存在する場合は一旦削除
DROP USER IF EXISTS 'Django_Developer_User'@'%';

-- ユーザーを作成
CREATE USER 'Django_Developer_User'@'%' IDENTIFIED BY 'Django_Developer_Password';

-- 権限を付与
GRANT ALL PRIVILEGES ON AI_API_DB.* TO 'Django_Developer_User'@'%';
GRANT ALL PRIVILEGES ON test_AI_API_DB.* TO 'Django_Developer_User'@'%';

-- 認証方式を設定
ALTER USER 'Django_Developer_User'@'%' IDENTIFIED WITH mysql_native_password BY 'Django_Developer_Password';

-- 権限を即時反映
FLUSH PRIVILEGES;