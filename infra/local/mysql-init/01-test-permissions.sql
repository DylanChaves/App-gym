-- Dedicated test schema privileges; Django creates and drops this schema during tests.
GRANT ALL PRIVILEGES ON gym_test.* TO 'gym_app'@'%';
